"""Database grants registry for alembic-utils.

This module generates PGGrantTable entities for all application tables,
ensuring the 'arive' database role has SELECT, INSERT, UPDATE, DELETE
permissions on all tables.

These grants are registered with alembic-utils so that:
1. Alembic autogenerate knows the grants should exist
2. New tables automatically get grants in migrations
3. Grants are never accidentally dropped

Usage in alembic/env.py:
    from app.base.grants import get_table_grants
    register_entities(get_table_grants())
"""

from alembic_utils.pg_grant_table import PGGrantTable
from sqlalchemy import create_engine, inspect

from app.utils.configure import config as app_config

# The database role used by the application at runtime
APP_DB_ROLE = "arive"

# Tables managed outside of alembic (SAQ manages its own)
EXCLUDED_TABLES = {"alembic_version", "saq_jobs", "saq_stats", "saq_versions"}


def get_table_grants() -> list[PGGrantTable]:
    """Generate PGGrantTable entities for all application tables.

    Returns grants for SELECT, INSERT, UPDATE, DELETE on all tables
    in the public schema, excluding system tables (alembic, saq).

    The grants are generated dynamically based on what tables exist
    in the database, so new tables will automatically be included.
    """
    grants: list[PGGrantTable] = []

    try:
        engine = create_engine(app_config.ADMIN_DB_URL)
        inspector = inspect(engine)

        for table_name in inspector.get_table_names(schema="public"):
            # Skip excluded tables
            if table_name in EXCLUDED_TABLES:
                continue

            # Get column names for this table
            columns = [col["name"] for col in inspector.get_columns(table_name, schema="public")]

            # Create grants for SELECT, INSERT, UPDATE (with columns)
            for grant_type in ["SELECT", "INSERT", "UPDATE"]:
                grants.append(
                    PGGrantTable(
                        schema="public",
                        table=table_name,
                        columns=columns,
                        role=APP_DB_ROLE,
                        grant=grant_type,
                        with_grant_option=False,
                    )
                )

            # DELETE grant doesn't have columns
            grants.append(
                PGGrantTable(
                    schema="public",
                    table=table_name,
                    columns=[],
                    role=APP_DB_ROLE,
                    grant="DELETE",
                    with_grant_option=False,
                )
            )

        engine.dispose()

    except Exception:
        # If we can't connect to DB (e.g., offline mode), return empty
        # This prevents errors during offline migrations
        pass

    return grants
