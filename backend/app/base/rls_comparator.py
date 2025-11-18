"""Alembic comparator for detecting RLS state changes.

This comparator checks whether tables that should have RLS actually have it enabled,
and generates migrations to enable/disable RLS as needed.
"""

from __future__ import annotations

from sqlalchemy import text

from app.base.rls_operations import DisableRLSOp, EnableRLSOp


def compare_rls(
    autogen_context,
    upgrade_ops,
    schema,
    tablename,
    metadata_table,
    *args,
    **kwargs,
):
    """Compare RLS state between metadata and database.

    This comparator is called by Alembic autogenerate for each table.
    It checks:
    1. Does the metadata indicate this table should have RLS?
    2. Does the database currently have RLS enabled on this table?
    3. If there's a mismatch, generate the appropriate migration operation.

    Args:
        autogen_context: Alembic autogenerate context
        upgrade_ops: List to append upgrade operations to
        schema: Schema name (or None for default schema)
        tablename: Table name to check
        metadata_table: SQLAlchemy Table metadata object
        *args: Additional arguments (unused)
        **kwargs: Additional keyword arguments (unused)
    """
    # Skip if table doesn't exist in metadata
    if metadata_table is None:
        return

    # Use default schema if not specified
    schema = schema or "public"

    # Check metadata: should this table have RLS?
    # Tables that use RLS mixins register themselves in metadata.info["rls"]
    rls_tables = autogen_context.metadata.info.get("rls", set())
    should_have_rls = tablename in rls_tables

    # Check database: does this table currently have RLS enabled?
    connection = autogen_context.connection
    result = connection.execute(
        text(
            """
            SELECT t.rowsecurity::boolean as rls_enabled,
                   c.relforcerowsecurity::boolean as force_rls
            FROM pg_tables t
            JOIN pg_class c ON c.relname = t.tablename
            JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schemaname
            WHERE t.schemaname = :schema
              AND t.tablename = :tablename
        """
        ),
        {"schema": schema, "tablename": tablename},
    )

    row = result.fetchone()
    has_rls = row and row[0]  # rowsecurity column
    has_force_rls = row and row[1]  # relforcerowsecurity column

    # Generate migration operations if there's a mismatch
    if should_have_rls and not has_rls:
        # Table should have RLS but doesn't - enable it
        upgrade_ops.ops.append(EnableRLSOp(schema, tablename, force=True))
    elif has_rls and not should_have_rls:
        # Table has RLS but shouldn't - disable it
        upgrade_ops.ops.append(DisableRLSOp(schema, tablename))
    elif should_have_rls and has_rls and not has_force_rls:
        # Table has RLS but not FORCE - we want FORCE enabled
        # Disable and re-enable with force
        upgrade_ops.ops.append(DisableRLSOp(schema, tablename))
        upgrade_ops.ops.append(EnableRLSOp(schema, tablename, force=True))
