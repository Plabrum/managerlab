"""Custom Alembic operations for Row-Level Security management.

This module provides custom Alembic operations to enable/disable RLS on tables,
allowing autogenerate to detect when RLS needs to be enabled or disabled.

Usage in migrations:
    op.enable_rls('public', 'campaigns')
    op.disable_rls('public', 'campaigns')
"""

from __future__ import annotations

from alembic.autogenerate import renderers
from alembic.operations import MigrateOperation, Operations


class EnableRLSOp(MigrateOperation):
    """Operation to enable Row-Level Security on a table."""

    def __init__(self, schema: str, tablename: str, force: bool = True):
        """Initialize RLS enable operation.

        Args:
            schema: Database schema name (e.g., 'public')
            tablename: Table name to enable RLS on
            force: Whether to force RLS even for table owner (default: True)
        """
        self.schema = schema
        self.tablename = tablename
        self.force = force

    def reverse(self):
        """Return the reverse operation (disable RLS)."""
        return DisableRLSOp(self.schema, self.tablename)


class DisableRLSOp(MigrateOperation):
    """Operation to disable Row-Level Security on a table."""

    def __init__(self, schema: str, tablename: str):
        """Initialize RLS disable operation.

        Args:
            schema: Database schema name (e.g., 'public')
            tablename: Table name to disable RLS on
        """
        self.schema = schema
        self.tablename = tablename

    def reverse(self):
        """Return the reverse operation (enable RLS with force)."""
        return EnableRLSOp(self.schema, self.tablename, force=True)


# Implementation functions
def _impl_enable_rls(operations, operation):
    """Execute ENABLE ROW LEVEL SECURITY on the database."""
    operations.execute(f"ALTER TABLE {operation.schema}.{operation.tablename} ENABLE ROW LEVEL SECURITY")
    if operation.force:
        operations.execute(f"ALTER TABLE {operation.schema}.{operation.tablename} FORCE ROW LEVEL SECURITY")


def _impl_disable_rls(operations, operation):
    """Execute DISABLE ROW LEVEL SECURITY on the database."""
    # Disable force first, then disable RLS
    operations.execute(f"ALTER TABLE {operation.schema}.{operation.tablename} NO FORCE ROW LEVEL SECURITY")
    operations.execute(f"ALTER TABLE {operation.schema}.{operation.tablename} DISABLE ROW LEVEL SECURITY")


# Register implementations
Operations.implementation_for(EnableRLSOp)(_impl_enable_rls)
Operations.implementation_for(DisableRLSOp)(_impl_disable_rls)


# Add convenience methods to Operations class
def enable_rls(self, schema: str, tablename: str, force: bool = True):
    """Enable RLS on a table - convenience method for migrations."""
    op = EnableRLSOp(schema, tablename, force)
    return self.invoke(op)


def disable_rls(self, schema: str, tablename: str):
    """Disable RLS on a table - convenience method for migrations."""
    op = DisableRLSOp(schema, tablename)
    return self.invoke(op)


# Attach methods to Operations class
Operations.enable_rls = enable_rls
Operations.disable_rls = disable_rls


@renderers.dispatch_for(EnableRLSOp)
def render_enable_rls(autogen_context, op):
    """Render enable_rls operation in migration files."""
    force_param = f", force={op.force}" if not op.force else ""
    return f"op.enable_rls('{op.schema}', '{op.tablename}'{force_param})"


@renderers.dispatch_for(DisableRLSOp)
def render_disable_rls(autogen_context, op):
    """Render disable_rls operation in migration files."""
    return f"op.disable_rls('{op.schema}', '{op.tablename}')"
