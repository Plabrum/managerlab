"""Pytest configuration and fixtures for backend tests.

This is the main conftest.py file that sets up the test environment and imports
all fixtures from the fixtures/ package.

All fixtures are organized into logical modules:
- fixtures.database: Database engine, sessions, and RLS helpers
- fixtures.dependencies: Dependency injection providers and mock clients
- fixtures.app: Litestar app and test client fixtures
- fixtures.auth: Authentication and authorization fixtures
- fixtures.factories: Factory helpers for creating complex objects
- fixtures.common: Common object fixtures (user, team, brand, etc.)
"""

import logging
import os

# ============================================================================
# Environment Setup
# ============================================================================
# CRITICAL: Set test environment BEFORE any app imports
# This must happen first to ensure all modules use test configuration

os.environ.setdefault("ENV", "testing")

# Silence httpx INFO logs during tests
logging.getLogger("httpx").setLevel(logging.WARNING)

# ============================================================================
# Model Discovery
# ============================================================================
# Import and discover all models before tests run
# This ensures SQLAlchemy knows about all models for migrations and queries

from app.utils.discovery import discover_and_import

discover_and_import(["models.py", "models/**/*.py"], base_path="app")

# ============================================================================
# Import All Fixtures
# ============================================================================
# Import all fixtures from the fixtures package to make them available to tests
# Using star imports here is intentional for pytest fixture discovery

from tests.fixtures import *  # noqa: F401, F403
