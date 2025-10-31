from litestar.logging import LoggingConfig

from app.utils.configure import config

# Environment-aware logging configuration
# Development: RichHandler with colors and formatting for nice local experience
# Production: StreamHandler with standard Python tracebacks for CloudWatch

if config.IS_DEV:
    # Development: Use RichHandler for nice formatting
    console_handler = {
        "class": "rich.logging.RichHandler",
        "markup": True,
        "rich_tracebacks": True,
        "show_time": False,
        "show_path": False,
    }
else:
    # Production: Use StreamHandler with standard format for CloudWatch
    console_handler = {
        "class": "logging.StreamHandler",
        "formatter": "standard",
        "stream": "ext://sys.stdout",
    }

logging_config = LoggingConfig(
    formatters={
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    handlers={
        "console": console_handler,
        "queue_listener": {
            "class": "logging.handlers.QueueHandler",
            "queue": {"()": "queue.Queue", "maxsize": -1},
            "listener": "litestar.logging.standard.LoggingQueueListener",
            "handlers": ["console"],
        },
    },
)
logger = logging_config.configure()()
