"""remove_all_rls_policies

Revision ID: 62374ba3d425
Revises: 323d5b52334f
Create Date: 2025-11-17 16:39:12.223928

This migration removes all RLS policies and disables RLS on all tables.
This is a cleanup migration to allow regenerating policies with the correct configuration.

Changes:
1. Drop all team_scope_policy policies from team-scoped tables
2. Drop all dual_scope_policy policies from dual-scoped tables
3. Remove FORCE ROW LEVEL SECURITY from all tables
4. Disable ROW LEVEL SECURITY on all tables

Note: The downgrade function is intentionally left empty as new policies will be
created in subsequent migrations.
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "62374ba3d425"
down_revision: Union[str, Sequence[str], None] = "323d5b52334f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tables with team_scope_policy
TEAM_SCOPED_TABLES = [
    "brand_contacts",
    "brands",
    "campaigns",
    "dashboards",
    "events",
    "payment_blocks",
    "roster",
    "threads",
]

# Tables with dual_scope_policy
DUAL_SCOPED_TABLES = [
    "deliverable_media",
    "deliverables",
    "documents",
    "invoices",
    "media",
    "messages",
]

# All tables that have RLS enabled
ALL_RLS_TABLES = TEAM_SCOPED_TABLES + DUAL_SCOPED_TABLES


def upgrade() -> None:
    """Remove all RLS policies and disable RLS."""

    # Drop team_scope_policy from team-scoped tables
    for table in TEAM_SCOPED_TABLES:
        op.execute(f"DROP POLICY IF EXISTS team_scope_policy ON {table}")

    # Drop dual_scope_policy from dual-scoped tables
    for table in DUAL_SCOPED_TABLES:
        op.execute(f"DROP POLICY IF EXISTS dual_scope_policy ON {table}")

    # Disable FORCE RLS and RLS on all tables
    for table in ALL_RLS_TABLES:
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    """Downgrade schema.

    Intentionally left empty as new RLS policies will be created
    in subsequent migrations with the correct configuration.
    """
    pass
