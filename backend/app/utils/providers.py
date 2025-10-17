from typing import AsyncGenerator
import aiohttp
from litestar import Litestar
from litestar.datastructures import State
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from litestar_saq import TaskQueues
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import raiseload
from sqlalchemy.pool import NullPool

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.sessions.store import PostgreSQLSessionStore
from app.utils.configure import config, Config
from app.actions.registry import ActionRegistry
from app.objects.base import ObjectRegistry
from app.client.s3_client import S3Dep


async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    from app.auth.scope_context import get_request_scope
    from app.base.scope_mixins import TeamScopedMixin, DualScopedMixin
    from litestar.exceptions import PermissionDeniedException

    # Listener that injects scope filters and soft delete filters into every ORM SELECT
    def _apply_filters(execute_state):
        if not execute_state.is_select:
            return

        statement = execute_state.statement

        # Get the model from the statement
        from_clause = list(statement.get_final_froms())
        if not from_clause:
            return

        # Get the mapped class (model)
        mapper = from_clause[0]
        if not hasattr(mapper, "entity"):
            return

        model = mapper.entity

        # Apply soft delete filter (all models have deleted_at from BaseDBModel)
        if hasattr(model, "deleted_at"):
            statement = statement.where(model.deleted_at.is_(None))

        # Apply scope filter
        scope = get_request_scope()
        if scope:
            # Check if model uses scope mixins
            is_team_scoped = issubclass(model, TeamScopedMixin)
            is_dual_scoped = issubclass(model, DualScopedMixin)

            if is_dual_scoped:
                # DualScopedMixin: Has both team_id and campaign_id
                if scope.is_team_scoped:
                    # Team scope: Filter by team_id
                    statement = statement.where(model.team_id == scope.team_id)
                elif scope.is_campaign_scoped:
                    # Campaign scope: Filter by campaign_id
                    statement = statement.where(model.campaign_id == scope.campaign_id)

            elif is_team_scoped:
                # TeamScopedMixin: Has only team_id
                if scope.is_team_scoped:
                    # Team scope: Filter by team_id
                    statement = statement.where(model.team_id == scope.team_id)
                elif scope.is_campaign_scoped:
                    # Campaign guests cannot access team-only resources
                    raise PermissionDeniedException(
                        f"Campaign guests cannot access {model.__name__} resources"
                    )

        # Also apply raiseload for eager loading enforcement
        statement = statement.options(raiseload("*"))

        execute_state.statement = statement

    # Attach the listener to THIS session only
    event.listen(db_session.sync_session, "do_orm_execute", _apply_filters)
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(status_code=HTTP_409_CONFLICT, detail=str(exc)) from exc
    finally:
        # Always remove the listener so it doesn't leak to other sessions
        event.remove(db_session.sync_session, "do_orm_execute", _apply_filters)


async def on_startup(app: Litestar) -> None:
    app.state.http = aiohttp.ClientSession()


async def on_shutdown(app: Litestar) -> None:
    await app.state.http.close()


def provide_http(state: State) -> aiohttp.ClientSession:
    return state.http


def create_postgres_session_store() -> PostgreSQLSessionStore:
    """Provide PostgreSQL session store."""

    # Create engine for session store
    engine = create_async_engine(
        config.ASYNC_DATABASE_URL,
        poolclass=NullPool,
        connect_args={
            "connect_timeout": 10,
            "application_name": "manageros-sessions",
        },
        pool_pre_ping=False,
    )

    # Create session factory
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
        autobegin=True,
    )

    return PostgreSQLSessionStore(session_factory)


def provide_action_registry(
    s3_client: S3Dep, config: Config, transaction: AsyncSession, task_queues: TaskQueues
) -> ActionRegistry:
    return ActionRegistry(
        s3_client=s3_client,
        config=config,
        transaction=transaction,
        task_queues=task_queues,
    )


def provide_object_registry(s3_client: S3Dep, config: Config) -> ObjectRegistry:
    """Provide the ObjectRegistry singleton with dependencies."""
    return ObjectRegistry(s3_client=s3_client, config=config)
