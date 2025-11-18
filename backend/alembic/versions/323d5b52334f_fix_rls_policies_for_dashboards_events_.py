"""fix_rls_policies_for_dashboards_events_payment_blocks

Revision ID: 323d5b52334f
Revises: dffe5d0201e5
Create Date: 2025-11-17 16:04:36.150375

This migration fixes RLS policies for three tables that were created with old/incorrect
policy definitions:
- dashboards
- events
- payment_blocks

These tables had policies that:
1. Allowed access when app.team_id IS NULL (insecure)
2. Did not check app.is_system_mode for system bypass

This migration updates them to match the standard team_scope_policy format.
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "323d5b52334f"
down_revision: Union[str, Sequence[str], None] = "dffe5d0201e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tables that need their RLS policies fixed
TABLES_TO_FIX = ["dashboards", "events", "payment_blocks"]


def upgrade() -> None:
    """Upgrade schema - fix RLS policies."""
    for table in TABLES_TO_FIX:
        # Drop the old policy
        op.execute(f"DROP POLICY IF EXISTS team_scope_policy ON {table}")

        # Create the correct policy with NULL checks and system mode bypass
        op.execute(
            f"""
            CREATE POLICY team_scope_policy ON {table}
            AS PERMISSIVE
            FOR ALL
            USING (
                (current_setting('app.team_id', true) IS NOT NULL
                 AND team_id = current_setting('app.team_id', true)::int)
                OR current_setting('app.is_system_mode', true)::boolean IS TRUE
            )
        """
        )


def downgrade() -> None:
    """Downgrade schema - restore old insecure policies."""
    for table in TABLES_TO_FIX:
        # Drop the new policy
        op.execute(f"DROP POLICY IF EXISTS team_scope_policy ON {table}")

        # Restore the old insecure policy (for rollback purposes only)
        op.execute(
            f"""
            CREATE POLICY team_scope_policy ON {table}
            AS PERMISSIVE
            FOR ALL
            USING (
                team_id = current_setting('app.team_id', true)::int
                OR current_setting('app.team_id', true) IS NULL
            )
        """
        )
