"""Main application entry point."""

from app.utils.configure import config
from app.utils.discovery import discover_and_import

# Discover models first for SQLAlchemy
discover_and_import(["models.py", "models/**/*.py"], base_path="app")

from app.factory import create_app

# Create app (logging configured via LoggingConfig in factory)
app = create_app(config=config)
