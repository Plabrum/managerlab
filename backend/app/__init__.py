"""Application package helpers."""

from importlib import import_module
from typing import Iterable

from app.utils.discovery import discover_and_import


def load_all_models(extra_modules: Iterable[str] | None = None) -> None:
    """Import all SQLAlchemy model modules to register mappers.

    This function uses auto-discovery to find and import all models.py files
    in the application. This is critical for Alembic's autogenerate feature
    to detect all model changes.

    Models are automatically registered via BaseDBModel.__init_subclass__,
    so we just need to ensure the modules are imported.

    Args:
        extra_modules: Optional additional module paths to import manually
    """
    # Auto-discover all models.py files and models/ subdirectories
    discover_and_import(["models.py", "models/**/*.py"], base_path="app")

    # Import any extra modules provided
    if extra_modules:
        for module_path in extra_modules:
            import_module(module_path)


__all__ = ["load_all_models"]
