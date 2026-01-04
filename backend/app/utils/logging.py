"""Logging utilities for OpenTelemetry trace correlation.

This module provides:
- OTELTraceContextFilter: Adds trace_id and span_id for distributed tracing correlation
- create_logging_config(): Factory function for Litestar LoggingConfig
"""

import logging

from litestar.logging import LoggingConfig

from app.utils.configure import ConfigProtocol


class OTELTraceContextFilter(logging.Filter):
    """Inject OpenTelemetry trace context (trace_id, span_id) into log records.

    This filter enables correlation between logs and distributed traces by adding
    trace_id and span_id to every log record. In Betterstack and other observability
    tools, you can use these IDs to jump from logs to traces and vice versa.

    Attributes added to LogRecord:
        trace_id (str | None): 32-character hex string (128-bit trace ID)
        span_id (str | None): 16-character hex string (64-bit span ID)
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Add OTEL trace context to log record.

        Retrieves the current span from OpenTelemetry's context and extracts
        trace_id and span_id. If no active span exists or OTEL is not installed,
        sets these fields to None.

        Args:
            record: The log record to modify

        Returns:
            True (always allow the log record to be emitted)
        """
        try:
            from opentelemetry import trace

            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                ctx = span.get_span_context()
                # Format as hex strings for readability
                record.trace_id = format(ctx.trace_id, "032x")  # type: ignore[attr-defined]
                record.span_id = format(ctx.span_id, "016x")  # type: ignore[attr-defined]
            else:
                record.trace_id = None  # type: ignore[attr-defined]
                record.span_id = None  # type: ignore[attr-defined]
        except ImportError:
            # OpenTelemetry not installed or disabled
            record.trace_id = None  # type: ignore[attr-defined]
            record.span_id = None  # type: ignore[attr-defined]
        return True


def create_logging_config(config: ConfigProtocol) -> LoggingConfig:
    """Create Litestar LoggingConfig based on environment.

    Args:
        config: Application configuration

    Returns:
        LoggingConfig for development (Rich) or production (structured text)
    """
    if config.IS_DEV:
        # Development: Rich console output with trace correlation and clean stack traces
        return LoggingConfig(
            filters={
                "otel_trace_context": {
                    "()": "app.utils.logging.OTELTraceContextFilter",
                },
            },
            handlers={
                "console": {
                    "class": "rich.logging.RichHandler",
                    "filters": ["otel_trace_context"],
                    "rich_tracebacks": True,
                    "tracebacks_suppress": [
                        "litestar",
                        "starlette",
                        "uvicorn",
                        "anyio",
                        "httpx",
                    ],
                    "tracebacks_show_locals": True,
                    "markup": False,
                    "show_time": False,  # Compact format - timestamps not needed with --reload
                    "show_level": True,
                    "show_path": True,
                },
            },
            loggers={
                "uvicorn.access": {"level": "WARNING"},  # Quiet uvicorn access logs
            },
        )
    else:
        # Production: Structured text with OTEL trace correlation
        return LoggingConfig(
            filters={
                "otel_trace_context": {
                    "()": "app.utils.logging.OTELTraceContextFilter",
                },
            },
            formatters={
                "production": {
                    "format": (
                        "%(asctime)s [%(levelname)s] %(name)s - %(message)s "
                        "| trace_id=%(trace_id)s span_id=%(span_id)s"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            handlers={
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "production",
                    "filters": ["otel_trace_context"],
                    "level": config.LOG_LEVEL,
                },
            },
            loggers={
                "uvicorn.access": {"level": "WARNING"},
            },
        )
