"""Main application entry point."""

from app.utils.discovery import discover_and_import

# Discover and import all models before app initialization
discover_and_import(["models.py", "models/**/*.py"], base_path="app")

import logging
from typing import Any

from litestar import Response, get

from app.actions.routes import action_router
from app.auth.routes import auth_router
from app.brands.routes import brand_router
from app.campaigns.routes import campaign_router
from app.dashboard.routes import dashboard_router
from app.deliverables.routes import deliverable_router
from app.documents.routes.documents import document_router
from app.factory import create_app
from app.media.routes import local_media_router, media_router
from app.objects.routes import object_router
from app.payments.routes import invoice_router
from app.roster.routes import roster_router
from app.teams.routes import team_router
from app.threads import thread_router
from app.threads.websocket import thread_handler
from app.users.routes import user_router
from app.utils.configure import config

logger = logging.getLogger(__name__)


@get("/health", tags=["system"], guards=[])
async def health_check() -> Response:
    """Health check endpoint."""
    return Response(content={"detail": "ok"}, status_code=200)


# Build route handlers list with conditional local media router
route_handlers: list[Any] = [
    health_check,
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
    thread_router,
    thread_handler,
]

# Only include local media router in development
if config.IS_DEV:
    route_handlers.append(local_media_router)

# Create the application using the factory
# All configuration is handled automatically based on config.ENV
app = create_app(
    route_handlers=route_handlers,
    config=config,
)

logger.info(f"✅ ManagerLab API initialized successfully. Environment: {config.ENV}")
