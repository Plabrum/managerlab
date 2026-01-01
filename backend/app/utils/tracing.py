"""Explicit tracing decorator for business logic operations."""

import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def trace_operation[T](
    operation_name: str,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Trace async operations with explicit operation name.

    Usage:
        @trace_operation("user.create")
        async def create_user(name: str) -> User:
            ...

    The decorator creates a span with the given name and records:
    - Success/error status
    - Exception details on failure
    - Execution duration (automatic)

    Args:
        operation_name: Explicit name for the span (e.g., "action.trigger", "email.send")

    Returns:
        Decorator that wraps the async function
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            with tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("code.function", func.__qualname__)
                span.set_attribute("code.namespace", func.__module__)

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
