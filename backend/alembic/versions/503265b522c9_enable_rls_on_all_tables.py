"""enable_rls_on_all_tables

Revision ID: 503265b522c9
Revises: de32f5095333
Create Date: 2025-11-16 11:33:12.473784

This migration enables Row-Level Security (RLS) on all tables with team_id or campaign_id columns.

CRITICAL: This is the missing piece that makes RLS actually work. Policies were created but never
activated because RLS was never enabled on the tables.

Changes:
1. Enable RLS on all team-scoped tables (campaigns, brands, roster, etc.)
2. Force RLS even for table owners (security best practice)
3. Policies will now be enforced on all SELECT, INSERT, UPDATE, DELETE operations
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "503265b522c9"
down_revision: Union[str, Sequence[str], None] = "de32f5095333"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# All tables with team_id (team-scoped)
TEAM_SCOPED_TABLES = [
    "campaigns",
    "brands",
    "brand_contacts",
    "roster",
    "documents",
    "invoices",
    "threads",
]

# All tables with both team_id and campaign_id (dual-scoped)
DUAL_SCOPED_TABLES = [
    "deliverables",
    "messages",
    "media",
    "deliverable_media",
    "events",
]


def upgrade() -> None:
    """Enable RLS on all tables with team_id or campaign_id."""

    # Enable RLS on team-scoped tables
    for table in TEAM_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        # Force RLS even for table owners (postgres superuser)
        # This ensures RLS is always enforced, even in admin/system contexts
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    # Enable RLS on dual-scoped tables
    for table in DUAL_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")


def downgrade() -> None:
    """Disable RLS on all tables."""

    # Disable RLS on team-scoped tables
    for table in TEAM_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    # Disable RLS on dual-scoped tables
    for table in DUAL_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
