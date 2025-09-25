import logging
from advanced_alchemy.exceptions import RepositoryError
from litestar import Litestar, Response, get
from litestar.config.cors import CORSConfig
from litestar.contrib.sqlalchemy.plugins import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
    EngineConfig,
)
from litestar.di import Provide
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.security.session_auth import SessionAuth
from litestar.middleware.session.server_side import (
    ServerSideSessionConfig,
    ServerSideSessionBackend,
)
from litestar.middleware.session.base import ONE_DAY_IN_SECONDS
from app.base.models import BaseDBModel
from sqlalchemy.pool import NullPool

from app.utils.configure import config
from app.users.routes import user_router, public_user_router
from app.auth.routes import auth_router
from app.objects.routes import object_router

from app.utils.exceptions import ApplicationError, exception_to_http_response
from app.utils import providers
from app.utils.logging import logging_config


logger = logging.getLogger(__name__)


@get("/health", tags=["system"], guards=[])
async def health_check() -> Response:
    logger.info("Health check endpoint called")
    return Response(content={"detail": "ok"}, status_code=200)


session_auth = SessionAuth[int, ServerSideSessionBackend](
    session_backend_config=ServerSideSessionConfig(
        samesite="none",  # Required for cross-origin requests
        secure=config.ENV != "development",  # False for localhost, True for production
        httponly=True,  # Security: prevent XSS access to cookies
        max_age=ONE_DAY_IN_SECONDS * 14,  # 14 days
        domain=config.SESSION_COOKIE_DOMAIN,  # Configurable via env var
    ),
    retrieve_user_handler=lambda session, conn: session.get("user_id"),
    exclude=[
        "^/health",
        "^/auth/google/",
        "^/users/signup",
        "^/schema",
    ],
)


app = Litestar(
    route_handlers=[
        health_check,
        public_user_router,
        user_router,
        auth_router,
        object_router,
    ],
    on_startup=[providers.on_startup],
    on_shutdown=[providers.on_shutdown],
    on_app_init=[session_auth.on_app_init],
    middleware=[session_auth.middleware],  # Add this line
    logging_config=logging_config,
    cors_config=CORSConfig(
        allow_origins=[config.FRONTEND_ORIGIN],
        allow_credentials=True,  # Required for session cookies
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    ),
    exception_handlers={
        ApplicationError: exception_to_http_response,
        RepositoryError: exception_to_http_response,
    },
    stores={"sessions": providers.create_postgres_session_store()},
    dependencies={
        "transaction": Provide(providers.provide_transaction),
        "http_client": Provide(providers.provide_http, sync_to_thread=False),
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
    openapi_config=OpenAPIConfig(
        title="ManagerLab",
        description="Private schema of ManagerLab with Scalar OpenAPI docs",
        version="0.0.1",
        render_plugins=[ScalarRenderPlugin()],
    ),
)

logger.info(f"✅ ManageLab API initialized successfully Environment: {config.ENV}")
