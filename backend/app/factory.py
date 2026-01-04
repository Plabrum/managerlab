import logging
from typing import Any

from advanced_alchemy.exceptions import RepositoryError
from litestar import Litestar, Request, Response
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.psycopg import PsycoPgChannelsBackend
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.di import Provide
from litestar.exceptions import InternalServerException
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.middleware.session.base import ONE_DAY_IN_SECONDS
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins.sqlalchemy import (
    AsyncSessionConfig,
    EngineConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from litestar.security.session_auth import SessionAuth
from litestar.stores.memory import MemoryStore
from litestar.template.config import TemplateConfig
from litestar_saq import SAQConfig, SAQPlugin
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.actions.deps import provide_action_registry
from app.actions.routes import action_router
from app.auth.routes import auth_router
from app.base.models import BaseDBModel
from app.base.routes import system_router
from app.brands.routes import brand_router
from app.campaigns.routes import campaign_router
from app.client.openai_client import provide_openai_client
from app.client.s3_client import provide_s3_client
from app.dashboard.routes import dashboard_router
from app.deliverables.routes import deliverable_router
from app.documents.routes.documents import document_router
from app.emails.client import provide_email_client
from app.emails.webhook_routes import inbound_email_router
from app.media.routes import local_media_router, media_router
from app.objects.routes import object_router
from app.payments.routes import invoice_router
from app.plugins import SqidSchemaPlugin
from app.queue.config import queue_config
from app.roster.routes import roster_router
from app.teams.routes import team_router
from app.threads import thread_router
from app.threads.websocket import thread_handler
from app.users.routes import user_router
from app.utils import providers
from app.utils.configure import ConfigProtocol
from app.utils.exceptions import ApplicationError, exception_to_http_response
from app.utils.logging import create_logging_config
from app.utils.sqids import Sqid, sqid_dec_hook, sqid_enc_hook, sqid_type_predicate
from app.views.routes import view_router

logger = logging.getLogger(__name__)


def handle_options_disconnect(request: Request, exc: InternalServerException) -> Response:
    """Suppress client disconnect errors for OPTIONS preflight requests."""
    if request.method == "OPTIONS" and "client disconnected prematurely" in str(exc.detail):
        return Response(content=None, status_code=204)
    raise exc


def _shutdown_otel_if_enabled(config: ConfigProtocol) -> None:
    """Lazily import and shutdown OpenTelemetry if enabled."""
    if config.OTEL_ENABLED:
        from app.utils.otel import shutdown_opentelemetry

        shutdown_opentelemetry()


def create_app(
    config: ConfigProtocol,
    dependencies_overrides: dict[str, Provide] | None = None,
    plugins_overrides: list[Any] | None = None,
    stores_overrides: dict[str, Any] | None = None,
    skip_otel_init: bool = False,
) -> Litestar:
    # Initialize OpenTelemetry BEFORE creating Litestar app (if enabled)
    if not skip_otel_init:
        from app.utils.otel import initialize_opentelemetry

        initialize_opentelemetry(config)

    # ========================================================================
    # Logging Configuration
    # ========================================================================
    logging_config = create_logging_config(config)

    # ========================================================================
    # Stores
    # ========================================================================
    stores = {
        "sessions": providers.create_postgres_session_store(),
        "viewers": MemoryStore(),
    } | (stores_overrides or {})

    # ========================================================================
    # Session Auth
    # ========================================================================
    exclude_patterns = [
        "^/health",
        "^/auth/google/",
        "^/auth/magic-link/",
        "^/auth/logout",
        "^/webhooks/emails",
        "^/teams/invitations/accept",
        "^/schema",
    ]

    if config.IS_DEV:
        exclude_patterns.extend(["^/local-upload/", "^/local-download/"])

    session_auth = SessionAuth[int, Any](
        session_backend_config=ServerSideSessionConfig(
            samesite="lax",
            secure=not config.IS_DEV,
            httponly=True,
            max_age=ONE_DAY_IN_SECONDS * 14,
            domain=(config.SESSION_COOKIE_DOMAIN if hasattr(config, "SESSION_COOKIE_DOMAIN") else None),
        ),
        retrieve_user_handler=lambda session, conn: session.get("user_id"),
        exclude=exclude_patterns,
    )

    # ========================================================================
    # Dependencies
    # ========================================================================
    def _provide_s3_client() -> Any:
        return provide_s3_client(config)

    def _provide_openai_client(s3_client: Any) -> Any:
        return provide_openai_client(config, s3_client)

    dependencies = {
        "transaction": Provide(providers.provide_transaction),
        "http_client": Provide(providers.provide_http, sync_to_thread=False),
        "config": Provide(lambda: config, sync_to_thread=False),
        "s3_client": Provide(_provide_s3_client, sync_to_thread=False),
        "openai_client": Provide(_provide_openai_client, sync_to_thread=False),
        "email_client": Provide(provide_email_client, sync_to_thread=False),
        "email_service": Provide(providers.provide_email_service, sync_to_thread=False),
        "action_registry": Provide(provide_action_registry, sync_to_thread=False),
        "object_registry": Provide(providers.provide_object_registry, sync_to_thread=False),
        "team_id": Provide(providers.provide_team_id, sync_to_thread=False),
        "campaign_id": Provide(providers.provide_campaign_id, sync_to_thread=False),
        "viewer_store": Provide(providers.provide_viewer_store, sync_to_thread=False),
    } | (dependencies_overrides or {})

    # ========================================================================
    # Plugins
    # ========================================================================
    base_plugins = [
        SQLAlchemyPlugin(
            config=SQLAlchemyAsyncConfig(
                connection_string=config.ASYNC_DATABASE_URL,
                metadata=BaseDBModel.metadata,
                engine_config=EngineConfig(
                    poolclass=AsyncAdaptedQueuePool,
                    pool_size=0,  # Zero persistent connections for Aurora scale-to-zero
                    max_overflow=20,  # Create up to 20 temporary connections on-demand
                    pool_timeout=30,
                    connect_args={
                        "connect_timeout": 10,
                        "application_name": "manageros-ecs",
                    },
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
                web_enabled=config.IS_DEV,
                use_server_lifespan=True,
            )
        ),
        ChannelsPlugin(
            backend=PsycoPgChannelsBackend(config.ADMIN_DB_URL),
            arbitrary_channels_allowed=True,
        ),
        SqidSchemaPlugin(),
        # NO STRUCTLOG PLUGIN - Using stdlib logging configured above
    ]

    # Add OpenTelemetry plugin if enabled
    if config.OTEL_ENABLED:
        otel_config = OpenTelemetryConfig(
            tracer_provider=None,  # Uses global from otel.py
            meter_provider=None,  # Uses global from otel.py
            # Exclude health check endpoints from traces/metrics
            # These endpoints are high-frequency and don't need observability
            exclude=["/health", "/db_health"],
        )
        base_plugins.append(OpenTelemetryPlugin(config=otel_config))

    plugins: list[Any] = base_plugins if not plugins_overrides else plugins_overrides

    # ========================================================================
    # OpenAPI
    # ========================================================================

    openapi_config = OpenAPIConfig(
        title="Arive API",
        description="Arive API with OpenAPI documentation",
        version="0.0.2",
        render_plugins=[ScalarRenderPlugin()],
    )

    # ========================================================================
    # CORS
    # ========================================================================
    cors_config = CORSConfig(
        allow_origins=([config.FRONTEND_ORIGIN] if hasattr(config, "FRONTEND_ORIGIN") else ["*"]),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # ========================================================================
    # Template Engine
    # ========================================================================
    template_config = TemplateConfig(
        directory=config.EMAIL_TEMPLATES_DIR,
        engine=JinjaTemplateEngine,
    )

    # ========================================================================
    # Route Handlers
    # ========================================================================
    route_handlers: list[Any] = [
        system_router,
        user_router,
        team_router,
        roster_router,
        auth_router,
        object_router,
        action_router,
        brand_router,
        campaign_router,
        deliverable_router,
        media_router,
        document_router,
        invoice_router,
        dashboard_router,
        view_router,
        thread_router,
        thread_handler,
        inbound_email_router,
    ]
    if config.IS_DEV:
        route_handlers.append(local_media_router)

    # ========================================================================
    # Create App
    # ========================================================================
    app = Litestar(
        route_handlers=list(route_handlers),
        on_startup=[providers.on_startup],
        on_shutdown=[
            providers.on_shutdown,
            lambda: _shutdown_otel_if_enabled(config),
        ],
        on_app_init=[session_auth.on_app_init],
        middleware=[
            session_auth.middleware,
            LoggingMiddlewareConfig(
                exclude=["/health", "/db_health"],  # Skip health check endpoints
                request_log_fields=["method", "path", "query"],
                response_log_fields=["status_code"],
            ).middleware,
        ],
        cors_config=cors_config,
        exception_handlers={
            ApplicationError: exception_to_http_response,
            RepositoryError: exception_to_http_response,
            InternalServerException: handle_options_disconnect,
        },
        stores=stores,
        dependencies=dependencies,
        plugins=plugins,
        openapi_config=openapi_config,
        template_config=template_config,
        type_encoders={Sqid: sqid_enc_hook},
        type_decoders=[(sqid_type_predicate, sqid_dec_hook)],
        debug=config.IS_DEV,
        logging_config=logging_config,  # Use Litestar's standard logging with Rich in dev
    )

    return app
