#!/usr/bin/env python3
"""
Database migration script with advisory locking.

This script runs database migrations on container startup with proper
locking to prevent concurrent migrations from multiple containers.
"""

import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from alembic import command
from alembic.config import Config as AlembicConfig
from app.utils.configure import config as app_config

# Advisory lock ID for migrations (arbitrary constant)
MIGRATION_LOCK_ID = 123456789


def acquire_advisory_lock(engine, timeout_seconds: int = 300) -> bool:
    """
    Acquire a PostgreSQL advisory lock for migrations.

    Args:
        engine: SQLAlchemy engine
        timeout_seconds: Maximum time to wait for lock

    Returns:
        bool: True if lock acquired, False if timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        with engine.connect() as conn:
            # Try to acquire the advisory lock (non-blocking)
            result = conn.execute(
                text("SELECT pg_try_advisory_lock(:lock_id)"),
                {"lock_id": MIGRATION_LOCK_ID},
            )
            acquired = result.scalar()

            if acquired:
                print(f"✓ Acquired migration lock (ID: {MIGRATION_LOCK_ID})")
                return True

        print(f"⏳ Waiting for migration lock... ({int(time.time() - start_time)}s)")
        time.sleep(2)

    print(f"✗ Failed to acquire migration lock after {timeout_seconds}s")
    return False


def release_advisory_lock(engine) -> None:
    """Release the PostgreSQL advisory lock."""
    with engine.connect() as conn:
        conn.execute(text("SELECT pg_advisory_unlock(:lock_id)"), {"lock_id": MIGRATION_LOCK_ID})
        print(f"✓ Released migration lock (ID: {MIGRATION_LOCK_ID})")


def wait_for_database(max_retries: int = 30, retry_delay: int = 2) -> None:
    """
    Wait for database to be available.

    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between retries
    """
    database_url = app_config.DATABASE_URL

    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✓ Database connection established")
            engine.dispose()
            return
        except OperationalError as e:
            if attempt == max_retries:
                print(f"✗ Failed to connect to database after {max_retries} attempts")
                print(f"Error: {e}")
                sys.exit(1)

            print(f"⏳ Database not ready, retrying... ({attempt}/{max_retries})")
            time.sleep(retry_delay)


def run_migrations() -> None:
    """Run database migrations with advisory locking."""
    print("=" * 60)
    print("Starting database migration process")
    print("=" * 60)

    # Wait for database to be available
    print("\n[1/4] Checking database connectivity...")
    wait_for_database()

    database_url = app_config.DATABASE_URL
    engine = create_engine(database_url)

    try:
        # Acquire advisory lock
        print("\n[2/4] Acquiring migration lock...")
        if not acquire_advisory_lock(engine):
            print("✗ Could not acquire lock - another migration may be in progress")
            sys.exit(1)

        # Run migrations
        print("\n[3/4] Running Alembic migrations...")
        alembic_cfg = AlembicConfig("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✓ Migrations completed successfully")

        # Release lock
        print("\n[4/4] Releasing migration lock...")
        release_advisory_lock(engine)

        print("\n" + "=" * 60)
        print("✓ Migration process completed successfully")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        # Attempt to release lock on failure
        try:
            release_advisory_lock(engine)
        except Exception:
            pass
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_migrations()
