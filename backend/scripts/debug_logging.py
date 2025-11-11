#!/usr/bin/env python3
"""
Debug logging configuration interactively.

Usage:
  # From ECS exec shell:
  python3 -i scripts/debug_logging.py

  # Then in the Python shell:
  >>> test_logging()
  >>> check_handlers()
  >>> send_test_log()
  >>> test_vector_directly()
"""

import json
import logging
import socket
import sys
from datetime import datetime, timezone

import structlog

# Import app components
from app.utils.configure import config
from app.utils.logging import VectorTCPHandler, prod_logging_config, prod_structlog_plugin


def check_handlers():
    """Check what handlers are configured for the root logger."""
    print("\n=== Root Logger Configuration ===")
    root_logger = logging.getLogger()
    print(f"Root logger level: {logging.getLevelName(root_logger.level)}")
    print(f"Root logger handlers: {len(root_logger.handlers)}")

    for i, handler in enumerate(root_logger.handlers):
        print(f"\nHandler {i}: {handler.__class__.__name__}")
        print(f"  Level: {logging.getLevelName(handler.level)}")
        print(f"  Formatter: {handler.formatter}")

        if isinstance(handler, VectorTCPHandler):
            print(f"  Connected: {handler.connected}")
            print(f"  Logs sent: {handler.logs_sent}")
            print(f"  Connection attempts: {handler.connection_attempts}")
            print(f"  Last error: {handler.last_error}")

    print("\n=== Structlog Configuration ===")
    try:
        logger = structlog.get_logger()
        print(f"Structlog logger type: {type(logger)}")
        print(f"Structlog processors: {structlog.get_config()}")
    except Exception as e:
        print(f"Error getting structlog config: {e}")


def test_logging():
    """Test logging with both stdlib and structlog."""
    print("\n=== Testing Standard Library Logging ===")
    stdlib_logger = logging.getLogger("test_stdlib")
    stdlib_logger.info("Test message from stdlib logger")
    stdlib_logger.warning("Test warning from stdlib logger")

    print("\n=== Testing Structlog ===")
    struct_logger = structlog.get_logger("test_structlog")
    struct_logger.info(
        "Test message from structlog", test_field="test_value", timestamp=datetime.now(tz=timezone.utc).isoformat()
    )
    struct_logger.warning("Test warning from structlog", test_field="warning_value")

    print("\nLogs sent. Check CloudWatch and BetterStack.")


def send_test_log():
    """Send a test log directly through the VectorTCPHandler."""
    print("\n=== Sending Test Log via VectorTCPHandler ===")

    # Find VectorTCPHandler
    root_logger = logging.getLogger()
    vector_handler = None

    for handler in root_logger.handlers:
        if isinstance(handler, VectorTCPHandler):
            vector_handler = handler
            break

    if not vector_handler:
        print("ERROR: No VectorTCPHandler found!")
        print("Available handlers:", [h.__class__.__name__ for h in root_logger.handlers])
        return

    print(f"Found VectorTCPHandler - Connected: {vector_handler.connected}")

    # Create a test log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='{"event": "manual_test", "message": "Direct VectorTCPHandler test", "timestamp": "%s"}'
        % datetime.now(tz=timezone.utc).isoformat(),
        args=(),
        exc_info=None,
    )

    try:
        vector_handler.emit(record)
        print(f"✓ Log sent successfully. Total logs sent: {vector_handler.logs_sent}")
    except Exception as e:
        print(f"✗ Failed to send log: {e}")


def test_vector_directly():
    """Test sending directly to Vector via TCP socket."""
    print("\n=== Testing Direct Vector Connection ===")

    test_message = {
        "event": "direct_socket_test",
        "message": "Testing direct connection to Vector",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "level": "info",
    }

    try:
        sock = socket.create_connection(("localhost", 9000), timeout=2.0)
        data = json.dumps(test_message).encode("utf-8") + b"\n"
        sock.sendall(data)
        sock.close()
        print("✓ Successfully sent test message to Vector")
        print(f"  Message: {json.dumps(test_message, indent=2)}")
    except Exception as e:
        print(f"✗ Failed to connect to Vector: {e}")


def inspect_config():
    """Inspect the current logging configuration."""
    print("\n=== Logging Configuration Inspection ===")
    print(f"Environment: {config.ENV}")
    print(f"Is Dev: {config.IS_DEV}")

    print("\n--- prod_logging_config ---")
    print(f"Handlers: {list(prod_logging_config.handlers.keys())}")
    print(f"Loggers: {list(prod_logging_config.loggers.keys())}")

    print("\n--- prod_structlog_plugin ---")
    print(f"Plugin type: {type(prod_structlog_plugin)}")
    if hasattr(prod_structlog_plugin, "_config"):
        print(f"Config: {prod_structlog_plugin._config}")
    else:
        print("Config: <not accessible>")


def fix_logging():
    """Attempt to reconfigure logging to use VectorTCPHandler."""
    print("\n=== Attempting to Fix Logging Configuration ===")

    # Get root logger
    root_logger = logging.getLogger()

    # Remove existing handlers
    print(f"Removing {len(root_logger.handlers)} existing handlers...")
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add VectorTCPHandler directly
    print("Adding VectorTCPHandler...")
    vector_handler = VectorTCPHandler(host="localhost", port=9000)
    vector_handler.setLevel(logging.INFO)
    root_logger.addHandler(vector_handler)
    root_logger.setLevel(logging.INFO)

    print("✓ Logging reconfigured")
    print(f"  Root logger level: {logging.getLevelName(root_logger.level)}")
    print(f"  Handlers: {[h.__class__.__name__ for h in root_logger.handlers]}")

    # Test it
    print("\nTesting reconfigured logging...")
    test_logging()


def main():
    """Run all diagnostic checks."""
    print("=" * 60)
    print("Logging Debug Helper")
    print("=" * 60)

    inspect_config()
    check_handlers()
    test_vector_directly()

    print("\n" + "=" * 60)
    print("Available commands:")
    print("  check_handlers()      - Show current handler configuration")
    print("  test_logging()        - Send test logs via stdlib and structlog")
    print("  send_test_log()       - Send test log via VectorTCPHandler")
    print("  test_vector_directly()- Send test message directly to Vector socket")
    print("  inspect_config()      - Show logging configuration details")
    print("  fix_logging()         - Attempt to reconfigure logging")
    print("=" * 60)


if __name__ == "__main__":
    main()
