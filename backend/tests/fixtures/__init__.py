"""Test fixtures for backend tests.

This package organizes test fixtures into logical modules for better maintainability.

Pytest automatically discovers all fixtures defined in conftest.py and any modules
imported by it. By importing all fixture modules here and from the main conftest.py,
we make all fixtures available to tests while keeping them organized.
"""

# Import all fixtures to make them available to pytest
from .app import *  # noqa: F401, F403
from .common import *  # noqa: F401, F403
from .database import *  # noqa: F401, F403
from .dependencies import *  # noqa: F401, F403
from .factories import *  # noqa: F401, F403
