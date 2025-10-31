"""Module auto-discovery utility for automatic imports.

This module provides functionality to automatically discover and import Python
modules based on filename patterns. This is particularly useful for:

1. Models - Ensuring all SQLAlchemy models are imported for Alembic migrations
2. Tasks - Ensuring all task decorators are executed to register with the queue
3. Objects - Ensuring all object classes are loaded to register with ObjectRegistry

Example:
    from app.utils.discovery import discover_and_import

    # Discover all model files
    discover_and_import(["models.py"], base_path="app")

    # Discover all task files
    discover_and_import(["tasks.py"], base_path="app")

    # Discover all object files
    discover_and_import(["object.py", "*_object.py"], base_path="app")
"""

import logging
from importlib import import_module
from pathlib import Path

logger = logging.getLogger(__name__)


def discover_and_import(
    patterns: list[str],
    base_path: str = "app",
    exclude_paths: list[str] | None = None,
) -> list[str]:
    """
    Discover and import Python modules matching the given filename patterns.

    This function recursively searches for Python files matching the specified
    patterns and imports them. This is useful for ensuring decorator-based
    registration (like @task) or __init_subclass__ registration (like models
    and objects) gets executed.

    Special handling for subdirectories:
    - "models.py" matches app/users/models.py
    - "models/**/*.py" matches app/brands/models/brands.py, app/brands/models/contacts.py
    - "objects.py" matches app/brands/objects.py
    - "objects/**/*.py" matches app/users/objects/user.py, app/users/objects/roster.py

    Args:
        patterns: List of filename patterns to match (e.g., ["models.py", "models/**/*.py", "objects.py"])
        base_path: Base directory to search from (default: "app")
        exclude_paths: List of path segments to exclude (default: ["__pycache__", "test", "tests", "base"])

    Returns:
        List of imported module names

    Example:
        # Import all model files (including models/ subdirectories)
        modules = discover_and_import(["models.py", "models/**/*.py"])

        # Import all task and object files
        modules = discover_and_import(["tasks.py", "objects.py", "objects/**/*.py"])
    """
    if exclude_paths is None:
        exclude_paths = ["__pycache__", "test", "tests", "alembic"]

    # Get the backend directory (parent of app/)
    backend_dir = Path(__file__).parent.parent.parent
    search_dir = backend_dir / base_path

    if not search_dir.exists():
        logger.warning(f"Search directory does not exist: {search_dir}")
        return []

    imported_modules: list[str] = []
    seen_modules: set[str] = set()  # Avoid duplicate imports

    for pattern in patterns:
        # Find all files matching the pattern
        for file_path in search_dir.rglob(pattern):
            # Skip if file is in excluded paths
            if any(excluded in file_path.parts for excluded in exclude_paths):
                logger.debug(f"Skipping excluded file: {file_path}")
                continue

            # Skip __init__.py files
            if file_path.name == "__init__.py":
                continue

            # Convert file path to module name
            # e.g., /path/to/backend/app/users/models.py -> app.users.models
            # e.g., /path/to/backend/app/brands/models/brands.py -> app.brands.models.brands
            try:
                relative_path = file_path.relative_to(backend_dir)
                module_parts = list(relative_path.parts[:-1])  # Remove .py extension
                module_parts.append(relative_path.stem)  # Add filename without .py
                module_name = ".".join(module_parts)

                # Skip if already imported
                if module_name in seen_modules:
                    continue

                # Import the module
                logger.debug(f"Importing module: {module_name}")
                import_module(module_name)
                imported_modules.append(module_name)
                seen_modules.add(module_name)

            except Exception as e:
                logger.error(f"Failed to import {file_path}: {e}")
                continue

    logger.info(f"Auto-discovery imported {len(imported_modules)} modules for patterns {patterns}")
    return imported_modules
