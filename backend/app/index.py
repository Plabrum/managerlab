"""Main application entry point."""

# Configure logging FIRST - before any other imports

from app.logging_config import configure_logging
from app.utils.configure import config

configure_logging(config)

# Now do model discovery and other imports
from app.utils.discovery import discover_and_import

discover_and_import(["models.py", "models/**/*.py"], base_path="app")

from app.factory import create_app

app = create_app(config=config)

# Note: Startup logging happens in providers.on_startup()
