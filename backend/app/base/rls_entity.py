"""Custom alembic-utils entity for tracking RLS enablement on tables.

This allows Alembic autogenerate to detect when:
1. A table should have RLS enabled but doesn't
2. A table has RLS enabled but shouldn't
3. FORCE RLS setting changes

Usage:
    from app.base.rls_entity import PGRLSEnabled

    # Register for a table
    rls_entity = PGRLSEnabled(schema="public", table="campaigns", force=True)
"""

from __future__ import annotations

from typing import Any

from alembic_utils.replaceable_entity import ReplaceableEntity
from sqlalchemy import TextClause, text


class PGRLSEnabled(ReplaceableEntity):
    """Represents RLS enablement state for a PostgreSQL table.

    This custom alembic-utils entity tracks whether Row-Level Security is enabled
    on a table, allowing autogenerate to detect changes.

    Attributes:
        schema: Database schema (usually 'public')
        table: Table name
        force: Whether to force RLS even for table owner (recommended: True)
    """

    def __init__(
        self,
        schema: str,
        table: str,
        force: bool = True,
    ):
        """Initialize RLS enablement entity.

        Args:
            schema: Database schema name (e.g., 'public')
            table: Table name (e.g., 'campaigns')
            force: Whether to use FORCE ROW LEVEL SECURITY (default: True)
        """
        self.schema = schema
        self.table = table
        self.force = force

        # ReplaceableEntity requires schema, signature, and definition
        # For RLS enablement, we use a simple marker definition
        definition = f"ENABLED{' FORCED' if force else ''}"

        super().__init__(
            schema=schema,
            signature=table,  # Unique identifier for this entity
            definition=definition,  # Required by ReplaceableEntity
        )

    @classmethod
    def from_sql(cls, sql: str) -> PGRLSEnabled:
        """Parse SQL to create PGRLSEnabled instance.

        Not typically used for RLS entities since we don't parse from SQL,
        but required by ReplaceableEntity interface.
        """
        raise NotImplementedError("RLS entities are not created from SQL")

    def to_sql_statement_create(self) -> TextClause:
        """Generate SQL to enable RLS on the table.

        Returns:
            SQL statement(s) to enable RLS
        """
        statements = [f"ALTER TABLE {self.schema}.{self.table} ENABLE ROW LEVEL SECURITY"]

        if self.force:
            statements.append(f"ALTER TABLE {self.schema}.{self.table} FORCE ROW LEVEL SECURITY")

        return text(";\n".join(statements))

    def to_sql_statement_drop(self, cascade: bool = False) -> TextClause:
        """Generate SQL to disable RLS on the table.

        Args:
            cascade: Unused for RLS (kept for interface compatibility)

        Returns:
            SQL statement(s) to disable RLS
        """
        statements = []

        if self.force:
            statements.append(f"ALTER TABLE {self.schema}.{self.table} NO FORCE ROW LEVEL SECURITY")

        statements.append(f"ALTER TABLE {self.schema}.{self.table} DISABLE ROW LEVEL SECURITY")

        return text(";\n".join(statements))

    def get_compare_identity_query(self) -> str:
        """Get SQL query to check if this table exists.

        Returns:
            SQL query that returns rows if the table exists
        """
        return f"""
            SELECT schemaname, tablename
            FROM pg_tables
            WHERE schemaname = '{self.schema}'
              AND tablename = '{self.table}'
        """

    def get_database_definition(self, sess, **kwargs) -> PGRLSEnabled | None:  # type: ignore[override]
        """Get current RLS state from database.

        Args:
            sess: SQLAlchemy session/connection to query database
            **kwargs: Additional arguments (unused, for interface compatibility)

        Returns:
            PGRLSEnabled instance representing current DB state, or None if table doesn't exist
        """
        connection = sess
        # Query to check RLS state
        result = connection.execute(
            text(f"""
                SELECT
                    t.schemaname,
                    t.tablename,
                    t.rowsecurity::boolean as rls_enabled,
                    c.relforcerowsecurity::boolean as force_rls
                FROM pg_tables t
                JOIN pg_class c ON c.relname = t.tablename
                JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schemaname
                WHERE t.schemaname = '{self.schema}'
                  AND t.tablename = '{self.table}'
            """)
        )

        row = result.fetchone()
        if not row:
            return None

        rls_enabled = row[2]  # rowsecurity column
        force_rls = row[3]  # relforcerowsecurity column

        # If RLS is not enabled in DB, return None to indicate it should be created
        if not rls_enabled:
            return None

        # Return current state from database
        return PGRLSEnabled(
            schema=row[0],
            table=row[1],
            force=bool(force_rls) if force_rls is not None else False,
        )

    def is_equal_definition(self, other: PGRLSEnabled | None) -> bool:
        """Compare this entity with another to detect changes.

        Args:
            other: Another PGRLSEnabled instance or None

        Returns:
            True if entities are equivalent, False otherwise
        """
        if other is None:
            return False

        return (
            self.schema == other.schema
            and self.table == other.table
            and self.force == other.force
            and self.definition == other.definition
        )

    @property
    def identity(self) -> str:
        """Return unique identity string for this entity.

        Used by alembic-utils to track entities across migrations.
        """
        return f"{self.schema}.{self.table}"

    def __repr__(self) -> str:
        """String representation for debugging."""
        force_str = " FORCE" if self.force else ""
        return f"PGRLSEnabled({self.schema}.{self.table}{force_str})"

    def render_self_for_migration(self, omit_definition: bool = False) -> str:
        """Render Python code for migration file.

        This is what appears in the migration file when autogenerate detects changes.

        Args:
            omit_definition: Whether to omit the definition (unused for RLS)

        Returns:
            Python code string to create this entity
        """
        # Python code to recreate this entity
        # Note: Alembic will automatically add necessary imports
        return f'PGRLSEnabled(schema="{self.schema}", table="{self.table}", force={self.force})'
