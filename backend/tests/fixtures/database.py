"""Database-related test fixtures."""

import asyncio
import os
import subprocess
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from litestar.stores.memory import MemoryStore
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import raiseload
from sqlalchemy.pool import NullPool

from app.utils.configure import TestConfig
from app.utils.db_filters import soft_delete_filter

# ============================================================================
# Configuration & Utilities
# ============================================================================


@pytest.fixture
def memory_store() -> MemoryStore:
    """Provide a fresh MemoryStore instance for each test."""
    return MemoryStore()


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """Provide test configuration - created once per session."""
    return TestConfig()


@pytest.fixture(scope="session")
def test_engine(test_config: TestConfig):
    """Create a test database engine for the entire test session.

    Uses NullPool to create fresh connections for each checkout.
    """
    engine = create_async_engine(
        test_config.SQLALCHEMY_DB_URL,
        echo=False,
        poolclass=NullPool,  # Fresh connections for isolation
    )
    return engine


# ============================================================================
# Database Setup
# ============================================================================


@pytest.fixture(scope="session")
def setup_database(test_engine, test_config: TestConfig):
    """Set up test database schema by running Alembic migrations.

    Runs migrations once per test session using:
    - postgres user for migrations (schema modifications)
    - arive user for application runtime (RLS enforced)
    """
    # Create admin engine for schema operations (using postgres superuser)
    admin_engine = create_engine(test_config.MIGRATION_DB_URL, poolclass=NullPool)

    def _setup():
        # Drop and recreate schema to ensure clean state
        with admin_engine.begin() as conn:
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))

            # Create arive user if it doesn't exist
            conn.execute(
                text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'arive') THEN
                        CREATE USER arive WITH PASSWORD 'arive';
                    END IF;
                END
                $$;
            """)
            )

        # Run Alembic migrations with explicit ENV=testing
        # Note: We must copy os.environ and modify it rather than just passing {"ENV": "testing"}
        # because the subprocess needs other env vars like PATH, HOME, etc. to run properly
        result = subprocess.run(
            ["uv", "run", "alembic", "upgrade", "head"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
            env={**os.environ, "ENV": "testing"},
        )

        if result.returncode != 0:
            raise RuntimeError(f"Alembic migration failed:\n{result.stderr}")

        # Grant permissions to arive user
        with admin_engine.begin() as conn:
            conn.execute(text("GRANT USAGE ON SCHEMA public TO arive"))
            conn.execute(text("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arive"))
            conn.execute(text("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO arive"))
            conn.execute(
                text(
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO arive"
                )
            )
            conn.execute(text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO arive"))

    def _teardown():
        # Clean up at end of test session
        with admin_engine.begin() as conn:
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        admin_engine.dispose()
        asyncio.run(test_engine.dispose())

    # Run setup
    _setup()

    yield

    # Run teardown
    _teardown()


# ============================================================================
# Session Fixtures
# ============================================================================


@pytest.fixture
async def db_session(test_engine, setup_database) -> AsyncGenerator[AsyncSession]:
    """Provide a database session with system mode enabled for creating fixtures.

    System mode bypasses RLS policies so test fixtures can be created without
    requiring team/campaign context.

    This fixture just creates the session - no rollback logic here.
    The transaction fixture handles rollback and event listeners.
    """
    session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autobegin=True,
    )

    session = session_maker()

    # Enable system mode to bypass RLS for fixture creation
    await session.execute(text("SET LOCAL app.is_system_mode = true"))

    yield session

    # Just close the session, no rollback (transaction handles that)
    await session.close()


@pytest.fixture
async def transaction(db_session: AsyncSession, team) -> AsyncGenerator[AsyncSession]:
    """Provide a transaction with team-scoped RLS enforcement.

    This fixture:
    1. Sets team_id RLS variable and disables system mode
    2. Attaches event listeners (soft delete filter, raiseload)
    3. Yields the session for test use
    4. Removes event listeners
    5. Rolls back the transaction
    6. Restores system mode for cleanup

    Relies on:
    - db_session: Base session with system mode enabled
    - team: Team fixture from auth.py
    """
    await db_session.execute(text(f"SET LOCAL app.team_id = {int(team.id)}"))
    await db_session.execute(text("SET LOCAL app.is_system_mode = false"))
    yield db_session
