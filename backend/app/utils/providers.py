from typing import AsyncGenerator
import aiohttp
from litestar import Litestar
from litestar.datastructures import State
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import raiseload
from sqlalchemy.pool import NullPool

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.sessions.store import PostgreSQLSessionStore
from app.utils.configure import config


async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    # Listener that injects `raiseload("*")` into every ORM SELECT
    def _enforce_raiseload(execute_state):
        if execute_state.is_select:
            execute_state.statement = execute_state.statement.options(raiseload("*"))

    # Attach the listener to THIS session only
    event.listen(db_session.sync_session, "do_orm_execute", _enforce_raiseload)
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(status_code=HTTP_409_CONFLICT, detail=str(exc)) from exc
    finally:
        # Always remove the listener so it doesn't leak to other sessions
        event.remove(db_session.sync_session, "do_orm_execute", _enforce_raiseload)


async def on_startup(app: Litestar) -> None:
    app.state.http = aiohttp.ClientSession()

    # Initialize objects platform
    from app.objects.init import initialize_objects_platform

    initialize_objects_platform()


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
