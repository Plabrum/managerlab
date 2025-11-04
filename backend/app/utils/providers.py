from collections.abc import AsyncGenerator

import aiohttp
from litestar import Litestar, Request
from litestar.datastructures import State
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from litestar_saq import TaskQueues
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import raiseload
from sqlalchemy.pool import NullPool

from app.actions.registry import ActionRegistry
from app.client.s3_client import S3Dep
from app.objects.base import ObjectRegistry
from app.sessions.store import PostgreSQLSessionStore
from app.threads.services import ThreadViewerStore
from app.utils.configure import Config, config
from app.utils.db import set_rls_variables
from app.utils.db_filters import apply_soft_delete_filter


def provide_viewer_store(request: Request) -> ThreadViewerStore:
    """Provide ThreadViewerStore instance with injected MemoryStore."""
    return ThreadViewerStore(store=request.app.stores.get("viewers"))


async def provide_transaction(db_session: AsyncSession, request: Request) -> AsyncGenerator[AsyncSession]:
    """Provide a database transaction with RLS session variables and soft delete filtering."""

    def _raiseload_listener(execute_state):
        execute_state.statement = execute_state.statement.options(raiseload("*"))

    # --- Attach listeners to this specific session only ---
    event.listen(db_session.sync_session, "do_orm_execute", apply_soft_delete_filter)
    event.listen(db_session.sync_session, "do_orm_execute", _raiseload_listener)

    try:
        async with db_session.begin():
            await set_rls_variables(db_session, request)
            yield db_session

    except IntegrityError as exc:
        raise ClientException(status_code=HTTP_409_CONFLICT, detail=str(exc)) from exc

    finally:
        # --- Remove the same listener objects ---
        event.remove(db_session.sync_session, "do_orm_execute", apply_soft_delete_filter)
        event.remove(db_session.sync_session, "do_orm_execute", _raiseload_listener)


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
    s3_client: S3Dep,
    config: Config,
    transaction: AsyncSession,
    task_queues: TaskQueues,
    request: Request,
    team_id: int | None,
    campaign_id: int | None,
) -> ActionRegistry:
    return ActionRegistry(
        s3_client=s3_client,
        config=config,
        transaction=transaction,
        task_queues=task_queues,
        request=request,
        team_id=team_id,
        campaign_id=campaign_id,
        user=request.user,
    )


def provide_object_registry(s3_client: S3Dep, config: Config) -> ObjectRegistry:
    """Provide the ObjectRegistry singleton with dependencies."""
    return ObjectRegistry(s3_client=s3_client, config=config)


def provide_team_id(request: Request) -> int | None:
    """Provide the team ID from the session."""
    team_id = request.session.get("team_id")
    breakpoint()
    return int(team_id) if team_id else None


def provide_campaign_id(request: Request) -> int | None:
    """Provide the optional campaign ID from the session."""
    campaign_id = request.session.get("campaign_id")
    return int(campaign_id) if campaign_id else None
