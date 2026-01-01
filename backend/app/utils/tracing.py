"""Explicit tracing decorator for business logic operations."""

import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Span

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


type SpanEnricher = Callable[[Span, Any, Any], None]


def trace_operation[T](
    operation_name: str,
    *,
    enrich: SpanEnricher | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Trace async operations with explicit operation name and optional span enrichment.

    Usage:
        # Simple usage - just operation name
        @trace_operation("user_create")
        async def create_user(name: str) -> User:
            ...

        # With domain-specific enrichment
        def enrich_action_span(span: Span, args: tuple, kwargs: dict) -> None:
            if args and hasattr(args[0], 'group_type'):
                span.set_attribute("action.group", args[0].group_type.value)
            if object_id := kwargs.get('object_id'):
                span.set_attribute("action.object_id", object_id)

        @trace_operation("action_execution", enrich=enrich_action_span)
        async def trigger(self, data: Any, object_id: int | None = None):
            ...

    The decorator creates a span with the given name and records:
    - Success/error status
    - Exception details on failure
    - Execution duration (automatic)
    - Optional domain-specific attributes via enrich callback

    Args:
        operation_name: Explicit name for the span (e.g., "action_execution", "send_email")
        enrich: Optional callback to add domain-specific attributes to the span.
                Receives (span, args, kwargs) before function execution.

    Returns:
        Decorator that wraps the async function
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            with tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("code.function", func.__qualname__)
                span.set_attribute("code.namespace", func.__module__)

                # Allow domain-specific enrichment
                if enrich and span.is_recording():
                    try:
                        enrich(span, args, kwargs)
                    except Exception as e:
                        logger.debug(f"Span enrichment failed: {e}", exc_info=True)

                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("operation.status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("operation.status", "error")
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


def get_trace_context() -> dict[str, str]:
    """Get current trace_id and span_id for manual log correlation.

    Returns:
        Dict with "trace_id" and "span_id" keys (empty strings if no active span)
    """
    span = trace.get_current_span()
    if not span:
        return {"trace_id": "", "span_id": ""}

    ctx = span.get_span_context()
    if not ctx.is_valid:
        return {"trace_id": "", "span_id": ""}

    return {
        "trace_id": format(ctx.trace_id, "032x"),
        "span_id": format(ctx.span_id, "016x"),
    }
