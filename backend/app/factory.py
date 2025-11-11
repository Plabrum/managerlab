from collections.abc import Sequence
from typing import Any

from advanced_alchemy.exceptions import RepositoryError
from litestar import Litestar, Request, Response
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.psycopg import PsycoPgChannelsBackend
from litestar.config.cors import CORSConfig
from litestar.di import Provide
from litestar.exceptions import InternalServerException
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
from litestar_saq import SAQConfig, SAQPlugin
from sqlalchemy.pool import StaticPool

from app.actions.deps import provide_action_registry
from app.base.models import BaseDBModel
from app.client.s3_client import provide_s3_client
from app.emails.dependencies import provide_email_client, provide_email_service
from app.queue.config import queue_config
from app.utils import providers
from app.utils.configure import Config
from app.utils.exceptions import ApplicationError, exception_to_http_response
from app.utils.logging import dev_logging_config, prod_logging_config, prod_structlog_plugin
from app.utils.sqids import Sqid, sqid_dec_hook, sqid_enc_hook, sqid_type_predicate


def handle_options_disconnect(request: Request, exc: InternalServerException) -> Response:
    """Suppress client disconnect errors for OPTIONS preflight requests.

    CORS preflight OPTIONS requests have no body, so "client disconnected prematurely"
    errors during body parsing are expected and harmless. The CORS middleware has
    already handled the OPTIONS response correctly.
    """
    if request.method == "OPTIONS" and "client disconnected prematurely" in str(exc.detail):
        # Return empty 204 response (CORS middleware already sent the actual response)
        return Response(content=None, status_code=204)
    # Re-raise for actual errors
    raise exc


def create_app(
    route_handlers: Sequence[Any],
    config: Config,
    dependencies_overrides: dict[str, Provide] | None = None,
    plugins_overrides: list[Any] | None = None,
    stores_overrides: dict[str, Any] | None = None,
) -> Litestar:
    # ========================================================================
    # Stores
    # ========================================================================
    stores = {
        # in testing session_store = MemoryStore()
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
        "^/teams/invitations/accept",
        "^/schema",
    ]

    if config.IS_DEV:
        exclude_patterns.extend(
            [
                "^/local-upload/",
                "^/local-download/",
            ]
        )

    session_auth = SessionAuth[int, Any](
        session_backend_config=ServerSideSessionConfig(
            samesite="lax",
            secure=not config.IS_DEV,  # Secure cookies in production/testing
            httponly=True,
            max_age=ONE_DAY_IN_SECONDS * 14,
            domain=(config.SESSION_COOKIE_DOMAIN if hasattr(config, "SESSION_COOKIE_DOMAIN") else None),
        ),
        retrieve_user_handler=lambda session, conn: session.get("user_id"),
        exclude=exclude_patterns,
    )

    # ========================================================================
    # Dependencies - Defaults that can be overridden
    # ========================================================================
    dependencies = {
        "transaction": Provide(providers.provide_transaction),
        "http_client": Provide(providers.provide_http, sync_to_thread=False),
        "config": Provide(lambda: config, sync_to_thread=False),
        "s3_client": Provide(provide_s3_client, sync_to_thread=False),
        "email_client": Provide(provide_email_client, sync_to_thread=False),
        "email_service": Provide(provide_email_service, sync_to_thread=False),
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
                    poolclass=StaticPool,
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
                web_enabled=config.IS_DEV,
                use_server_lifespan=True,
            )
        ),
        ChannelsPlugin(
            # in tesing backend = MemoryChannelsBackend()
            backend=PsycoPgChannelsBackend(config.PSYCOPG_DATABASE_URL),
            arbitrary_channels_allowed=True,
        ),
    ]

    # Add structlog plugin only in production
    if not config.IS_DEV:
        base_plugins.insert(0, prod_structlog_plugin)

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
    # Logging Config
    # ========================================================================
    # In production, use the Vector handler for sending logs to BetterStack
    # In development, use the RichHandler console output
    logging_config = prod_logging_config if not config.IS_DEV else dev_logging_config

    # ========================================================================
    # Create App
    # ========================================================================
    app = Litestar(
        route_handlers=list(route_handlers),
        on_startup=[providers.on_startup],
        on_shutdown=[providers.on_shutdown],
        on_app_init=[session_auth.on_app_init],
        middleware=[session_auth.middleware],
        logging_config=logging_config,
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
        type_encoders={Sqid: sqid_enc_hook},
        type_decoders=[(sqid_type_predicate, sqid_dec_hook)],
        debug=config.IS_DEV,
    )

    return app
