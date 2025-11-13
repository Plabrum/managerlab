"""Main application entry point."""

from app.utils.discovery import discover_and_import

discover_and_import(["models.py", "models/**/*.py"], base_path="app")


import structlog

from app.factory import create_app
from app.utils.configure import config

logger = structlog.get_logger(__name__)

app = create_app(config=config)

logger.info(
    "ManagerLab API initialized successfully",
    environment=config.ENV,
    debug=config.IS_DEV,
)
