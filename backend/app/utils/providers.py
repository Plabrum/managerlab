from typing import AsyncGenerator
import aiohttp
from litestar import Litestar, Request
from litestar.datastructures import State
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from litestar_saq import TaskQueues
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.sessions.store import PostgreSQLSessionStore
from app.utils.configure import config, Config
from app.utils.db import set_rls_variables
from app.utils.db_filters import apply_soft_delete_filter
from app.actions.registry import ActionRegistry
from app.objects.base import ObjectRegistry
from app.client.s3_client import S3Dep


async def provide_transaction(
    db_session: AsyncSession, request: Request
) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database transaction with RLS session variables and soft delete filtering.

    Sets PostgreSQL session variables for Row-Level Security based on session scope:
    - app.team_id: Set when user has team scope
    - app.campaign_id: Set when user has campaign scope
    - Neither set for admin/system operations

    Also applies soft delete filtering via SQLAlchemy event listener.
    """
    # Attach soft delete filter listener to THIS session only
    event.listen(db_session.sync_session, "do_orm_execute", apply_soft_delete_filter)
    try:
        async with db_session.begin():
            # Set RLS session variables within the transaction
            await set_rls_variables(db_session, request)
            yield db_session
    except IntegrityError as exc:
        raise ClientException(status_code=HTTP_409_CONFLICT, detail=str(exc)) from exc
    finally:
        # Always remove the listener so it doesn't leak to other sessions
        event.remove(
            db_session.sync_session, "do_orm_execute", apply_soft_delete_filter
        )


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
) -> ActionRegistry:
    return ActionRegistry(
        s3_client=s3_client,
        config=config,
        transaction=transaction,
        task_queues=task_queues,
        request=request,
    )


def provide_object_registry(s3_client: S3Dep, config: Config) -> ObjectRegistry:
    """Provide the ObjectRegistry singleton with dependencies."""
    return ObjectRegistry(s3_client=s3_client, config=config)
