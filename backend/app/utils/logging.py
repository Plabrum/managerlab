import logging
import logging.handlers

import structlog
from litestar.logging.config import LoggingConfig, StructLoggingConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin

from app.utils.configure import config

# Environment-aware logging configuration
# Development: ConsoleRenderer with colors and formatting for nice local experience
# Production: JSONRenderer for structured logging sent to Vector sidecar → Betterstack


class VectorTCPHandler(logging.handlers.SocketHandler):
    """Custom TCP handler that sends JSON logs to Vector sidecar.

    In ECS, containers share the same network namespace, so we can send to localhost:9000.
    Falls back gracefully if Vector is not available (development mode).
    """

    def __init__(self, host="localhost", port=9000):
        super().__init__(host, port)
        # Don't let connection failures crash the app
        self.closeOnError = False

    def makePickle(self, record):  # noqa: N802
        """Override to send raw log message instead of pickled record."""
        # The message should already be JSON from structlog's JSONRenderer
        return record.getMessage().encode("utf-8") + b"\n"

    def handleError(self, record):  # noqa: N802
        """Silently ignore errors (Vector might not be running in dev)."""
        pass


def create_structlog_config() -> StructlogConfig:
    """Create structlog configuration based on environment."""

    # Shared processors for both environments
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.processors.StackInfoRenderer(),
    ]

    if config.IS_DEV:
        # Development: Use ConsoleRenderer for readable colored output
        # No Vector sidecar in development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
        standard_lib_logging_config = None  # Use default handlers
    else:
        # Production: Use JSONRenderer and send to Vector sidecar via TCP
        processors = shared_processors + [
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]

        # Configure standard lib logging to send to Vector sidecar on localhost:9000
        vector_handler = VectorTCPHandler(host="localhost", port=9000)
        vector_handler.setLevel(logging.INFO)

        standard_lib_logging_config = LoggingConfig(
            handlers={
                "vector": {
                    "()": lambda: vector_handler,
                }
            },
            loggers={
                "": {  # Root logger
                    "handlers": ["vector"],
                    "level": "INFO",
                }
            },
        )

    structlog_logging_config = StructLoggingConfig(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        standard_lib_logging_config=standard_lib_logging_config,
    )

    return StructlogConfig(
        structlog_logging_config=structlog_logging_config,
    )


structlog_config = create_structlog_config()
structlog_plugin = StructlogPlugin(config=structlog_config)
