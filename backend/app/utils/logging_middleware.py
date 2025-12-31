"""Logging middleware for request tracing (stdlib version)."""

import uuid

from litestar import Request
from litestar.enums import ScopeType
from litestar.exceptions import ImproperlyConfiguredException
from litestar.middleware import DefineMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send

from app.logging_config import request_id_var, user_id_var


class RequestLoggingMiddleware:
    """Middleware to add request ID and user ID to logging context."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Add request ID and user ID to context vars for the duration of the request."""
        scope_type = scope.get("type")

        # Only process HTTP requests
        if scope_type == ScopeType.HTTP:
            request = Request(scope=scope, receive=receive, send=send)
            request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

            # Set context variables
            request_id_var.set(request_id)

            # Add user_id if authenticated
            try:
                if request.user:
                    user_id_var.set(request.user)
            except (ImproperlyConfiguredException, AttributeError):
                # Auth middleware hasn't run yet or user not authenticated
                pass

            try:
                await self.app(scope, receive, send)
            finally:
                # Clear context after request
                request_id_var.set(None)
                user_id_var.set(None)
        else:
            # WebSocket, ASGI lifespan events, etc. - pass through
            await self.app(scope, receive, send)


def create_logging_middleware() -> DefineMiddleware:
    """Create the logging middleware definition."""
    return DefineMiddleware(RequestLoggingMiddleware)
