import logging
import socket
import threading

import structlog
from litestar.logging.config import LoggingConfig, StructLoggingConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin


def get_task_ip():
    return socket.gethostbyname(socket.gethostname())


class VectorTCPHandler(logging.Handler):
    """TCP handler with persistent connection to Vector sidecar."""

    def __init__(self, host: str | None = None, port: int = 9000, timeout: float = 0.5) -> None:
        super().__init__()
        self.host = host or get_task_ip()
        self.port = port
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self.lock: threading.Lock = threading.Lock()

    def _connect(self) -> None:
        """Establish connection to Vector."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)

    def emit(self, record: logging.LogRecord) -> None:
        """Send log to Vector, reconnecting if needed."""
        try:
            msg = self.format(record)
            data = msg.encode("utf-8") + b"\n"

            with self.lock:
                # Try with existing socket first
                if self.sock is None:
                    self._connect()

                # After _connect(), sock is guaranteed to be set (or exception raised)
                assert self.sock is not None
                try:
                    self.sock.sendall(data)
                except (BrokenPipeError, OSError):
                    # Socket failed, reconnect and retry once
                    self._connect()
                    assert self.sock is not None
                    self.sock.sendall(data)
        except Exception:
            # Silently drop if Vector unavailable
            pass

    def close(self) -> None:
        """Clean up socket on handler shutdown."""
        with self.lock:
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None
        super().close()


# Production: Use structlog with JSON logs sent to Vector over TCP via queue (non-blocking)
prod_structlog_plugin = StructlogPlugin(
    config=StructlogConfig(
        structlog_logging_config=StructLoggingConfig(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
            standard_lib_logging_config=LoggingConfig(
                handlers={
                    "vector": {
                        "()": VectorTCPHandler,
                        "host": "localhost",
                        "port": 9000,
                    },
                    "queue_listener": {
                        "class": "logging.handlers.QueueHandler",
                        "queue": {"()": "queue.Queue", "maxsize": -1},
                        "listener": "litestar.logging.standard.LoggingQueueListener",
                        "handlers": ["vector"],
                    },
                },
                loggers={"": {"handlers": ["queue_listener"], "level": "INFO"}},
            ),
        )
    )
)

# Development: Just use RichHandler with standard Python logging
dev_logging_config = LoggingConfig(
    handlers={
        "console": {
            "class": "rich.logging.RichHandler",
            "markup": True,
            "rich_tracebacks": True,
            "show_time": False,
            "show_path": False,
        },
        "queue_listener": {
            "class": "logging.handlers.QueueHandler",
            "queue": {"()": "queue.Queue", "maxsize": -1},
            "listener": "litestar.logging.standard.LoggingQueueListener",
            "handlers": ["console"],
        },
    },
)
