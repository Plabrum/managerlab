from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
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
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool
import psycopg

from app.config import config
from app.models.base import Base
from app.routes.users import user_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def log_any_exception(request: Request, exc: Exception) -> Response:
    logger.exception("Unhandled exception at %s: %s", request.url.path, exc)
    return Response(content={"detail": "Internal Server Error"}, status_code=500)


@get("/", tags=["system"])
async def root() -> dict:
    return {"status": "ok"}


@get("/health", tags=["system"])
async def health_check() -> dict:
    """Simple health check for App Runner - just returns 200 OK."""
    logger.info("Health check endpoint called")
    return {
        "status": "ok",
        "message": f"Service is running, {config.ASYNC_DATABASE_URL}",
    }


@get("/health/db", tags=["system"])
async def health_check_db(transaction: AsyncSession) -> dict:
    """Enhanced health check that validates database connectivity."""
    if not config.DATABASE_URL:
        logger.error("DATABASE_URL is not configured!")
        return {
            "status": "error",
            "message": "DATABASE_URL environment variable is not configured",
        }

    try:
        logger.info("Database URL: %s", config.DATABASE_URL)
        logger.info("Async Database URL: %s", config.ASYNC_DATABASE_URL)

        # Use the same db_session as the users endpoints
        result = await transaction.execute(text("SELECT 1"))
        logger.info("Database health check query result: %s", result.scalar())
        return {"status": "ok", "database": "connected"}

    except Exception as e:
        logger.error("Database health check failed: %s", str(e), exc_info=True)
        # Re-raise to get proper 500 status code
        raise


# Lazy, module-level cache so we don't pay creation every call
_sa_test_engine: AsyncEngine | None = None


@get("/health/db-sa", tags=["system"])
async def health_check_db_sa() -> dict:
    """
    Direct SQLAlchemy async engine test (bypasses Litestar SQLAlchemyPlugin & DI).
    Uses the same ASYNC_DATABASE_URL but constructs its own engine and runs SELECT 1.
    """
    global _sa_test_engine
    url = config.ASYNC_DATABASE_URL

    # ✅ Ensure this is async: e.g. 'postgresql+psycopg_async://' or 'postgresql+asyncpg://'
    if not url or "+async" not in url and "+asyncpg" not in url:
        # Quick sanity message to help debugging
        return {
            "status": "error",
            "message": (
                "ASYNC_DATABASE_URL must use an async dialect, e.g. "
                "'postgresql+psycopg_async://...' or 'postgresql+asyncpg://...'. "
                f"Got: {url!r}"
            ),
        }

    if _sa_test_engine is None:
        # Keep config aligned with your plugin; adjust connect_args per driver.
        # For psycopg3 async:
        connect_args = {
            "connect_timeout": 10,
            "server_settings": {"application_name": "manageros-lambda"},
        }
        # For asyncpg, prefer: connect_args = {"timeout": 10}

        _sa_test_engine = create_async_engine(
            url,
            echo=config.IS_DEV,
            poolclass=NullPool,  # Lambda-friendly: no lingering sockets
            connect_args=connect_args,  # Match driver (psycopg_async vs asyncpg)
            pool_pre_ping=False,  # Faster test path
        )

    try:
        async with _sa_test_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
        return {
            "status": "ok",
            "database": "connected_sqlalchemy_async",
            "test_result": value,
            "dialect": _sa_test_engine.dialect.name,
        }
    except Exception as e:
        logger.error("SQLAlchemy async direct test failed: %s", e, exc_info=True)
        raise


@get("/health/db-direct", tags=["system"])
async def health_check_db_direct() -> dict:
    """Direct database connection test using psycopg3 without SQLAlchemy DI."""
    try:
        logger.info("Testing direct database connection...")

        # Build connection string from config
        db_url = config.DATABASE_URL
        logger.info("Using DATABASE_URL: %s", db_url)

        # Convert SQLAlchemy URL to psycopg format if needed
        if db_url.startswith("postgresql://"):
            conn_string = db_url
        else:
            # Handle postgresql+psycopg:// format
            conn_string = db_url.replace("postgresql+psycopg://", "postgresql://")

        logger.info("Connecting with: %s", conn_string)

        # Direct async connection using psycopg3
        async with await psycopg.AsyncConnection.connect(conn_string) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1 as test_value")
                result = await cur.fetchone()

        logger.info("Direct DB test successful: %s", result)
        return {
            "status": "ok",
            "database": "connected_direct",
            "test_result": result[0] if result else None,
            "connection_type": "psycopg3_direct",
        }

    except Exception as e:
        logger.error("Direct database connection failed: %s", str(e), exc_info=True)
        raise


@get("/health/db-di", tags=["system"])
async def health_check_db_di(db_session: AsyncSession) -> dict:
    try:
        r = await db_session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected_di", "test_result": r.scalar()}
    except Exception as e:
        logger.error("DI session test failed: %s", e, exc_info=True)
        raise


async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(status_code=HTTP_409_CONFLICT, detail=str(exc)) from exc


sqlalchemy_plugin = SQLAlchemyPlugin(
    config=SQLAlchemyAsyncConfig(
        connection_string=config.ASYNC_DATABASE_URL,
        metadata=Base.metadata,
        engine_config=EngineConfig(
            poolclass=NullPool,  # recommended for Lambda
            connect_args={  # psycopg3-friendly
                "connect_timeout": 10,
                # optional: if Aurora enforces TLS
                # "sslmode": "require",
                # optional: label connections in pg_stat_activity
                "application_name": "manageros-lambda",
            },
            echo=config.IS_DEV,
            pool_pre_ping=False,  # saves a round-trip
        ),
        session_config=AsyncSessionConfig(
            expire_on_commit=False,
            autoflush=False,
            autobegin=True,
        ),
        create_all=False,  # run migrations yourself
    )
)

# Log startup information
logger.info("🚀 Starting ManageOS API")
logger.info(f"Environment: {config.ENV}")
logger.info(f"Database URL configured: {bool(config.DATABASE_URL)}")

app = Litestar(
    route_handlers=[
        root,
        health_check,
        health_check_db,
        health_check_db_direct,
        user_router,
    ],
    cors_config=CORSConfig(allow_origins=["*"]),
    exception_handlers={Exception: log_any_exception},
    dependencies={"transaction": Provide(provide_transaction)},
    plugins=[sqlalchemy_plugin],
)

logger.info("✅ ManageOS API initialized successfully")
