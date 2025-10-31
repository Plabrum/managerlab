"""Pytest configuration and fixtures for backend tests."""

import pytest
from litestar.stores.memory import MemoryStore


@pytest.fixture
def memory_store() -> MemoryStore:
    """Provide a fresh MemoryStore instance for each test."""
    return MemoryStore()
