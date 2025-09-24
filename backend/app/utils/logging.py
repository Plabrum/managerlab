from litestar.logging import LoggingConfig

logging_config = LoggingConfig(
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
    }
)
