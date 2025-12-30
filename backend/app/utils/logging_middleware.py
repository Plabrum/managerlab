"""Logging middleware for request tracing."""

import uuid

import structlog
from litestar import Request
from litestar.enums import ScopeType
from litestar.exceptions import ImproperlyConfiguredException
from litestar.middleware import DefineMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send
from structlog.types import EventDict


def drop_verbose_http_keys(_logger: object, _method_name: str, event_dict: EventDict) -> EventDict:
    """Structlog processor to remove verbose HTTP logging details.

    Filters out: cookies, body, headers
    Keeps: method, path, status_code, request_id, user_id, etc.
    """
    # Only filter HTTP response logs (identified by presence of status_code)
    if "status_code" not in event_dict:
        return event_dict

    # Remove verbose keys
    keys_to_drop = ["cookies", "body", "headers"]
    for key in keys_to_drop:
        event_dict.pop(key, None)

    return event_dict


def add_otel_trace_context(_logger: object, _method_name: str, event_dict: EventDict) -> EventDict:
    """Structlog processor to inject OpenTelemetry trace context into logs.

    Extracts trace_id and span_id from the current OpenTelemetry span context
    and adds them to the log record. This enables correlation between logs and traces.

    Format:
    - trace_id: 32-character hex string (e.g., "1234567890abcdef1234567890abcdef")
    - span_id: 16-character hex string (e.g., "1234567890abcdef")

    If no active span exists, these fields are omitted (doesn't add null values).
    """
    from opentelemetry import trace

    span = trace.get_current_span()
    if span is None:
        return event_dict

    span_ctx = span.get_span_context()
    if not span_ctx.is_valid:
        return event_dict

    # Add trace context in standard format
    event_dict["trace_id"] = format(span_ctx.trace_id, "032x")
    event_dict["span_id"] = format(span_ctx.span_id, "016x")

    return event_dict


class RequestLoggingMiddleware:
    """Middleware to add request ID to structlog context."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Add request ID and user ID to structlog context for the duration of the request."""
        # Get scope type - use .get() for safety since Litestar's Scope type doesn't include
        # all ASGI scope types (e.g., "lifespan")
        scope_type = scope.get("type")

        # Only process HTTP requests, delegate everything else
        match scope_type:
            case ScopeType.HTTP:
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

            case _:
                # WebSocket, ASGI lifespan events, or any other scope type - pass through
                await self.app(scope, receive, send)


def create_logging_middleware() -> DefineMiddleware:
    """Create the logging middleware definition."""
    return DefineMiddleware(RequestLoggingMiddleware)
