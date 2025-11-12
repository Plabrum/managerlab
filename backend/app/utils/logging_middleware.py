"""Logging middleware for request tracing."""

import uuid

import structlog
from litestar import Request
from litestar.datastructures import State
from litestar.exceptions import ImproperlyConfiguredException
from litestar.middleware import DefineMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send


class RequestLoggingMiddleware:
    """Middleware to add request ID to structlog context."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Add request ID and user ID to structlog context for the duration of the request."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract or generate request ID
        request = Request(scope=scope, receive=receive, send=send)
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Build context dict
        context = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        }

        # Add user_id if authenticated (may not be available yet before auth middleware)
        try:
            if request.user:
                context["user_id"] = request.user
        except (ImproperlyConfiguredException, AttributeError):
            # Auth middleware hasn't run yet or user not authenticated
            pass

        # Bind to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(**context)

        try:
            await self.app(scope, receive, send)
        finally:
            # Clear context after request
            structlog.contextvars.clear_contextvars()


def create_logging_middleware() -> DefineMiddleware:
    """Create the logging middleware definition."""
    return DefineMiddleware(RequestLoggingMiddleware)
