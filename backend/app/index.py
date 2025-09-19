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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool

from app.config import config
from app.base.models import Base
from app.users.routes import user_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def log_any_exception(request: Request, exc: Exception) -> Response:
    logger.exception("Unhandled exception at %s: %s", request.url.path, exc)
    return Response(content={"detail": "Internal Server Error"}, status_code=500)


@get("/health", tags=["system"])
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


# Log startup information
logger.info("🚀 Starting ManageOS API")
logger.info(f"Environment: {config.ENV}")
logger.info(f"Database URL configured: {bool(config.DATABASE_URL)}")

app = Litestar(
    route_handlers=[
        health_check,
        user_router,
    ],
    cors_config=CORSConfig(allow_origins=["*"]),
    exception_handlers={Exception: log_any_exception},
    dependencies={"transaction": Provide(provide_transaction)},
    plugins=[
        SQLAlchemyPlugin(
            config=SQLAlchemyAsyncConfig(
                connection_string=config.ASYNC_DATABASE_URL,
                metadata=Base.metadata,
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

logger.info("✅ ManageOS API initialized successfully")
