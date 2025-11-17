from __future__ import annotations

import re

from alembic_utils.replaceable_entity import ReplaceableEntity
from alembic_utils.reversible_op import CreateOp, ReplaceOp
from sqlalchemy import TextClause, text


def _validate_pg_identifier(identifier: str, name: str = "identifier") -> None:
    """Validate a PostgreSQL identifier to prevent SQL injection.

    PostgreSQL unquoted identifiers must:
    - Start with a letter (a-z) or underscore
    - Contain only letters, digits, underscores, and dollar signs
    - Be at most 63 characters long

    Args:
        identifier: The identifier to validate
        name: Name of the identifier for error messages

    Raises:
        ValueError: If identifier is invalid
    """
    if not identifier:
        raise ValueError(f"{name} cannot be empty")

    if len(identifier) > 63:
        raise ValueError(f"{name} '{identifier}' exceeds PostgreSQL's 63 character limit")

    # PostgreSQL identifier pattern: starts with letter or underscore,
    # followed by letters, digits, underscores, or dollar signs
    if not re.match(r"^[a-z_][a-z0-9_$]*$", identifier, re.IGNORECASE):
        raise ValueError(
            f"{name} '{identifier}' contains invalid characters. "
            "Must start with letter or underscore and contain only letters, digits, underscores, or dollar signs."
        )


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
        enabled: bool = True,
    ):
        """Initialize RLS enablement entity.

        Args:
            schema: Database schema name (e.g., 'public')
            table: Table name (e.g., 'campaigns')
            force: Whether to use FORCE ROW LEVEL SECURITY (default: True)
            enabled: Whether RLS is enabled at all (default: True)

        Raises:
            ValueError: If schema or table names are invalid PostgreSQL identifiers
        """
        # Validate identifiers to prevent SQL injection
        _validate_pg_identifier(schema, "schema")
        _validate_pg_identifier(table, "table")

        self.schema = schema
        self.table = table
        self.force = force
        self.enabled = enabled

        # ReplaceableEntity requires schema, signature, and definition
        # For RLS enablement, we use a simple marker definition
        if enabled:
            definition = f"ENABLED{' FORCED' if force else ''}"
        else:
            definition = "DISABLED"

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

    @classmethod
    def from_database(cls, connection, schema: str) -> list[PGRLSEnabled]:  # type: ignore[override]
        """Get all RLS-enabled tables from database for a given schema.

        Args:
            connection: SQLAlchemy connection to query database
            schema: Database schema name (e.g., 'public')

        Returns:
            List of PGRLSEnabled instances for all tables with RLS enabled
        """
        result = connection.execute(
            text(
                f"""
                SELECT
                    t.schemaname,
                    t.tablename,
                    t.rowsecurity::boolean as rls_enabled,
                    c.relforcerowsecurity::boolean as force_rls
                FROM pg_tables t
                JOIN pg_class c ON c.relname = t.tablename
                JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schemaname
                WHERE t.schemaname = '{schema}'
                  AND t.rowsecurity = true
            """
            )
        )

        entities = []
        for row in result:
            entities.append(
                cls(
                    schema=row[0],
                    table=row[1],
                    force=bool(row[3]) if row[3] is not None else False,
                    enabled=bool(row[2]),  # rowsecurity column
                )
            )

        return entities

    def to_sql_statement_create(self) -> TextClause:
        """Generate SQL to enable RLS on the table.

        Returns:
            SQL statement(s) to enable RLS
        """
        if not self.enabled:
            # If this entity represents disabled RLS, we shouldn't create anything
            # This happens when comparing against a DB where RLS is disabled
            return text("")

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
        if not self.enabled:
            # If this entity represents already-disabled RLS, we shouldn't drop anything
            return text("")

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

        # First check if table exists at all
        table_check = connection.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM pg_tables
                WHERE schemaname = '{self.schema}'
                  AND tablename = '{self.table}'
            """
            )
        )

        if table_check.fetchone()[0] == 0:
            # Table doesn't exist - skip this entity entirely
            # This prevents errors when models are defined but tables aren't created yet
            return None

        # Query to check RLS state
        result = connection.execute(
            text(
                f"""
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
            """
            )
        )

        row = result.fetchone()
        if not row:
            # Shouldn't happen since we already checked table exists, but be safe
            return None

        rls_enabled = row[2]  # rowsecurity column
        force_rls = row[3]  # relforcerowsecurity column

        # Always return an entity - if RLS is disabled, return with enabled=False
        # This prevents alembic-utils from crashing when trying to access .identity on None
        return PGRLSEnabled(
            schema=row[0],
            table=row[1],
            force=bool(force_rls) if force_rls is not None else False,
            enabled=bool(rls_enabled),
        )

    def get_required_migration_op(self, sess, dependencies=False):  # type: ignore[override]
        """Determine what migration operation is needed for this entity.

        Override to handle None from get_database_definition properly.
        """

        db_def = self.get_database_definition(sess)

        # If table doesn't exist or RLS is not enabled, create it
        if db_def is None:
            return CreateOp(self)

        # If definitions are equal, no operation needed
        if self.is_equal_definition(db_def):
            return None

        # Definitions differ, replace it
        return ReplaceOp(self)

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
            and self.enabled == other.enabled
            and self.definition == other.definition
        )

    @property
    def identity(self) -> str:
        """Return unique identity string for this entity.

        Used by alembic-utils to track entities across migrations.
        """
        return f"{self.schema}.{self.table}"

    @property
    def type_(self) -> str:
        """Return the type identifier for this entity.

        Required by ReplaceableEntity interface.
        """
        return "rls_enabled"

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
        var_name = self.to_variable_name()
        class_name = self.__class__.__name__

        # Only include enabled parameter if it's False (default is True)
        enabled_param = f",\n    enabled={self.enabled}" if not self.enabled else ""

        return f"""{var_name} = {class_name}(
    schema="{self.schema}",
    table="{self.table}",
    force={self.force}{enabled_param}
)
"""

    def to_variable_name(self) -> str:
        """Generate a variable name for this entity in migration files.

        Returns:
            Variable name like 'public_campaigns_rls'
        """
        return f"{self.schema}_{self.table}_rls"
