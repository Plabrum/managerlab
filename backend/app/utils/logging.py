import logging
import socket
import sys
import threading
import time

import structlog
from litestar.logging.config import LoggingConfig, StructLoggingConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin


class VectorTCPHandler(logging.Handler):
    """TCP handler with persistent connection to Vector sidecar."""

    def __init__(self, host: str = "localhost", port: int = 9000, timeout: float = 0.5) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self.lock: threading.Lock = threading.Lock()
        self.connection_attempts = 0
        self.last_error: Exception | None = None
        self.connected = False
        self.logs_sent = 0

        # Try to establish initial connection and report status
        try:
            self._connect()
            self.connected = True
            print(f"[VectorTCPHandler] Successfully connected to Vector at {host}:{port}", file=sys.stderr)
        except Exception as e:
            self.last_error = e
            print(f"[VectorTCPHandler] WARNING: Failed to connect to Vector at {host}:{port}: {e}", file=sys.stderr)
            print(f"[VectorTCPHandler] Logs will be dropped until Vector is available", file=sys.stderr)

    def _connect(self) -> None:
        """Establish connection to Vector."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

        self.connection_attempts += 1
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.connected = True

        # Log successful reconnection if this was a reconnect
        if self.connection_attempts > 1:
            print(f"[VectorTCPHandler] Reconnected to Vector (attempt #{self.connection_attempts})", file=sys.stderr)

    def emit(self, record: logging.LogRecord) -> None:
        """Send log to Vector, reconnecting if needed."""
        try:
            # Get the message - structlog already formatted it as JSON
            msg = record.getMessage()
            data = msg.encode("utf-8") + b"\n"

            with self.lock:
                # Try with existing socket first
                if self.sock is None:
                    self._connect()

                # After _connect(), sock is guaranteed to be set (or exception raised)
                assert self.sock is not None
                try:
                    self.sock.sendall(data)
                    self.logs_sent += 1
                    # Log every 10 successful sends for diagnostics
                    if self.logs_sent % 10 == 0:
                        print(f"[VectorTCPHandler] Sent {self.logs_sent} logs to Vector", file=sys.stderr)
                except (BrokenPipeError, OSError) as e:
                    # Socket failed, reconnect and retry once
                    self.connected = False
                    print(f"[VectorTCPHandler] Connection lost: {e}, reconnecting...", file=sys.stderr)
                    self._connect()
                    assert self.sock is not None
                    self.sock.sendall(data)
                    self.logs_sent += 1
        except Exception as e:
            # Track errors but don't crash the application
            self.last_error = e
            self.connected = False
            # Only log error every 100 failed attempts to avoid spam
            if self.connection_attempts % 100 == 0:
                print(
                    f"[VectorTCPHandler] ERROR: Failed to send log to Vector after {self.connection_attempts} attempts: {e}",
                    file=sys.stderr,
                )

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
prod_logging_config = LoggingConfig(
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
)

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
            # Don't set standard_lib_logging_config here - we pass it directly to Litestar
            # to avoid conflicts. Litestar will handle stdlib logging initialization.
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
