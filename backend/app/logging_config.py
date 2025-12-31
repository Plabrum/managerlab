"""Ultra-simplified logging configuration.

Development:
  - Pretty console output via stdlib logging
  - No OTLP export

Production:
  - Plain text to stdout (for container debugging)
  - OTLP export to Betterstack (structured telemetry)
  - NO JSON rendering (OTLP already provides structured logs)
"""

import logging
from contextvars import ContextVar

from app.utils.configure import ConfigProtocol

# Context variables for request tracing (set by middleware)
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[int | None] = ContextVar("user_id", default=None)


class RequestContextFilter(logging.Filter):
    """Inject request context (request_id, user_id) into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context variables to record if available."""
        record.request_id = request_id_var.get()  # type: ignore[attr-defined]
        record.user_id = user_id_var.get()  # type: ignore[attr-defined]
        return True


class OTELTraceContextFilter(logging.Filter):
    """Inject OpenTelemetry trace context (trace_id, span_id) into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add OTLP trace context if active span exists."""
        try:
            from opentelemetry import trace

            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                ctx = span.get_span_context()
                record.trace_id = format(ctx.trace_id, "032x")  # type: ignore[attr-defined]
                record.span_id = format(ctx.span_id, "016x")  # type: ignore[attr-defined]
            else:
                record.trace_id = None  # type: ignore[attr-defined]
                record.span_id = None  # type: ignore[attr-defined]
        except ImportError:
            record.trace_id = None  # type: ignore[attr-defined]
            record.span_id = None  # type: ignore[attr-defined]
        return True


class HealthCheckFilter(logging.Filter):
    """Filter out noisy health check endpoint logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Suppress logs containing health check paths."""
        message = record.getMessage()
        # Filter out logs that mention health endpoints
        if "/health" in message or "/db_health" in message:
            return False
        return True


_logging_configured = False  # Guard to prevent double configuration


def configure_logging(config: ConfigProtocol) -> None:
    """Configure Python logging based on environment.

    This function is idempotent - safe to call multiple times.
    Only the first call will actually configure logging.

    Development:
      - Pretty console output with colors
      - Shows: timestamp, level, logger name, message, context

    Production:
      - Plain text to stdout (for kubectl logs / CloudWatch)
      - OTLP export handles structured logs (no JSON needed)
      - Shows: timestamp, level, logger, message, request_id, user_id, trace_id

    Args:
        config: Application configuration
    """
    global _logging_configured
    if _logging_configured:
        return
    _logging_configured = True
    # Create console handler
    if config.IS_DEV:
        # Development: Use rich.logging.RichHandler for beautiful console output
        from rich.logging import RichHandler

        console_handler = RichHandler(
            rich_tracebacks=True,
            markup=False,
            show_time=True,
            show_level=True,
            show_path=True,
            tracebacks_show_locals=True,
            log_time_format="[%H:%M:%S]",
        )
        console_handler.setLevel(config.LOG_LEVEL)
    else:
        # Production: Plain text (OTLP provides structure)
        # Include trace_id for correlation with distributed traces
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
            " | request_id=%(request_id)s user_id=%(user_id)s trace_id=%(trace_id)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(config.LOG_LEVEL)

    # Add filters for context injection and noise reduction
    console_handler.addFilter(RequestContextFilter())
    console_handler.addFilter(OTELTraceContextFilter())
    console_handler.addFilter(HealthCheckFilter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.LOG_LEVEL)
    root_logger.handlers.clear()  # Remove any existing handlers
    root_logger.addHandler(console_handler)

    # Force all existing loggers to use the root handler
    # This ensures consistent formatting even for loggers created before this function runs
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger_obj = logging.getLogger(logger_name)
        logger_obj.handlers.clear()
        logger_obj.propagate = True
        logger_obj.setLevel(logging.NOTSET)  # Inherit from root

    # Disable Python's lastResort handler
    logging.lastResort = None  # type: ignore[assignment]

    # Quiet down verbose loggers in development
    if config.IS_DEV:
        logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.info(f"Logging configured for {config.ENV} environment (level={config.LOG_LEVEL})")
