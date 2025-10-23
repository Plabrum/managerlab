import logging
from typing import Any
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
from litestar_saq import SAQConfig, SAQPlugin
from app.base.models import BaseDBModel
from sqlalchemy.pool import NullPool

from app.queue.config import queue_config
from app.utils.configure import config
from app.users.routes import user_router, public_user_router
from app.auth.routes import auth_router
from app.objects.routes import object_router
from app.actions.routes import action_router
from app.brands.routes import brand_router
from app.campaigns.routes import campaign_router
from app.deliverables.routes import deliverable_router
from app.media.routes import media_router, local_media_router
from app.payments.routes import invoice_router
from app.dashboard.routes import dashboard_router
from app.threads import thread_router, ThreadWebSocketHandler
from app.utils.exceptions import ApplicationError, exception_to_http_response
from app.utils import providers
from app.utils.logging import logging_config
from app.client.s3_client import provide_s3_client


logger = logging.getLogger(__name__)


@get("/health", tags=["system"], guards=[])
async def health_check() -> Response:
    logger.info("Health check endpoint called")
    return Response(content={"detail": "ok"}, status_code=200)


session_auth = SessionAuth[int, ServerSideSessionBackend](
    session_backend_config=ServerSideSessionConfig(
        samesite="lax",
        secure=config.ENV != "development",
        httponly=True,
        max_age=ONE_DAY_IN_SECONDS * 14,
        domain=config.SESSION_COOKIE_DOMAIN,
    ),
    retrieve_user_handler=lambda session, conn: session.get("user_id"),
    exclude=[
        "^/health",
        "^/auth/google/",
        "^/users/signup",
        "^/schema",
        "^/local-upload/",
        "^/local-download/",
    ],
)


# Build route handlers list with conditional local media router
route_handlers: list[Any] = [
    health_check,
    public_user_router,
    user_router,
    auth_router,
    object_router,
    action_router,
    brand_router,
    campaign_router,
    deliverable_router,
    media_router,
    invoice_router,
    dashboard_router,
    thread_router,
    ThreadWebSocketHandler,
]

# Only include local media router in development
if config.IS_DEV:
    route_handlers.append(local_media_router)

app = Litestar(
    route_handlers=route_handlers,
    on_startup=[providers.on_startup],
    on_shutdown=[providers.on_shutdown],
    on_app_init=[session_auth.on_app_init],
    middleware=[
        session_auth.middleware,
    ],
    logging_config=logging_config,
    cors_config=CORSConfig(
        allow_origins=[config.FRONTEND_ORIGIN],
        allow_credentials=True,  # Required for session cookies
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
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
        "config": Provide(lambda: config, sync_to_thread=False),
        "s3_client": Provide(provide_s3_client, sync_to_thread=False),
        "action_registry": Provide(
            providers.provide_action_registry, sync_to_thread=False
        ),
        "object_registry": Provide(
            providers.provide_object_registry, sync_to_thread=False
        ),
        "team_id": Provide(providers.provide_team_id, sync_to_thread=False),
        "campaign_id": Provide(providers.provide_campaign_id, sync_to_thread=False),
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
                        "application_name": "manageros-ecs",
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
        ),
        SAQPlugin(
            config=SAQConfig(
                queue_configs=queue_config,
                web_enabled=config.IS_DEV,  # Enable web UI in development
                use_server_lifespan=True,  # Integrate with Litestar lifecycle
            )
        ),
    ],
    openapi_config=OpenAPIConfig(
        title="ManagerLab",
        description="Private schema of ManagerLab with Scalar OpenAPI docs",
        version="0.0.1",
        render_plugins=[ScalarRenderPlugin()],
    ),
)

logger.info(f"✅ ManageLab API initialized successfully Environment: {config.ENV}")
