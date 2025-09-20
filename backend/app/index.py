import logging
import sys
from typing import AsyncGenerator
from litestar import Litestar, Request, Response, get
from litestar.config.cors import CORSConfig
from litestar.contrib.sqlalchemy.plugins import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
    EngineConfig,
)
from litestar.di import Provide
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.security.session_auth import SessionAuth
from litestar.connection import ASGIConnection
from litestar.middleware.session.server_side import (
    ServerSideSessionConfig,
    ServerSideSessionBackend,
)
from litestar.stores.memory import MemoryStore
from app.base.models import BaseDBModel
from app.sessions.store import PostgreSQLSessionStore
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import select

import aiohttp
from app.config import Config, config
from app.users.routes import user_router
from app.auth.routes import auth_router
from app.users.models import User
from litestar.datastructures import State

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def log_any_exception(request: Request, exc: Exception) -> Response:
    logger.exception("Unhandled exception at %s: %s", request.url.path, exc)
    return Response(content={"detail": "Internal Server Error"}, status_code=500)


@get("/health", tags=["system"], guards=[])
async def health_check() -> dict:
    """Simple health check for App Runner - just returns 200 OK."""
    logger.info("Health check endpoint called")
    return {
        "status": "ok",
        "message": "Service is running",
    }


async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(status_code=HTTP_409_CONFLICT, detail=str(exc)) from exc


def provide_config() -> Config:
    """Provide the application configuration."""
    return config


async def current_user_from_session(
    session: dict, connection: ASGIConnection
) -> User | None:
    """Retrieve user from session."""
    user_id = session.get("user_id")
    if not user_id:
        return None

    # Get async session from connection dependencies
    async with connection.app.state.sqlalchemy_plugin.get_session() as db_session:
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        return result.scalar_one_or_none()


async def on_startup(app: Litestar) -> None:
    app.state.http = aiohttp.ClientSession()


def provide_http(state: State) -> aiohttp.ClientSession:
    return state.http


def provide_postgres_session_store() -> PostgreSQLSessionStore:
    """Provide PostgreSQL session store."""
    from app.config import config
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

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


# Session authentication configuration
# session_store = provide_postgres_session_store()
session_store = MemoryStore()
session_config = ServerSideSessionConfig()
session_auth = SessionAuth[User, ServerSideSessionBackend](
    session_backend_config=session_config,
    retrieve_user_handler=current_user_from_session,
    exclude=[
        "^/health",
        "^/auth/google/",
        "^/users/signup",  # Exclude user signup endpoint
    ],
)


app = Litestar(
    route_handlers=[
        health_check,
        user_router,
        auth_router,
    ],
    on_startup=[on_startup],
    on_app_init=[session_auth.on_app_init],
    cors_config=CORSConfig(allow_origins=["*"]),
    exception_handlers={Exception: log_any_exception},
    stores={"sessions": session_store},  # PostgreSQL session store
    dependencies={
        "transaction": Provide(provide_transaction),
        "http_client": Provide(provide_http, sync_to_thread=False),
        "app_config": Provide(provide_config, sync_to_thread=False),
    },
    plugins=[
        SQLAlchemyPlugin(
            config=SQLAlchemyAsyncConfig(
                connection_string=config.ASYNC_DATABASE_URL,
                metadata=BaseDBModel.metadata,
                engine_config=EngineConfig(
                    poolclass=NullPool,
                    connect_args={
                        "connect_timeout": 10,
                        "application_name": "manageros-lambda",
                    },
                    pool_pre_ping=False,
                ),
                session_config=AsyncSessionConfig(
                    expire_on_commit=False,
                    autoflush=False,
                    autobegin=True,
                ),
                create_all=False,
            )
        )
    ],
)

logger.info("\n✅ ManageLab API initialized successfully \nEnvironment: {config.ENV}")
