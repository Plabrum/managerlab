"""rename activity_events to events and simplify schema

Revision ID: dae53f291868
Revises: 2a7044f6b274
Create Date: 2025-10-24 13:56:11.288469

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dae53f291868"
down_revision: str | Sequence[str] | None = "2a7044f6b274"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename table
    op.rename_table("activity_events", "events")

    # Rename indexes
    op.execute("ALTER INDEX ix_activity_events_actor RENAME TO ix_events_actor")
    op.execute("ALTER INDEX ix_activity_events_actor_id RENAME TO ix_events_actor_id")
    op.execute("ALTER INDEX ix_activity_events_deleted_at RENAME TO ix_events_deleted_at")
    op.execute("ALTER INDEX ix_activity_events_team_created RENAME TO ix_events_team_created")
    op.execute("ALTER INDEX ix_activity_events_team_id RENAME TO ix_events_team_id")
    op.execute("ALTER INDEX ix_activity_events_team_object RENAME TO ix_events_team_object")

    # Drop old columns (message, changes, extra_metadata)
    op.drop_column("events", "message")
    op.drop_column("events", "changes")
    op.drop_column("events", "extra_metadata")

    # Add new event_data column
    op.add_column(
        "events",
        sa.Column("event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new column
    op.drop_column("events", "event_data")

    # Restore old columns
    op.add_column("events", sa.Column("message", sa.Text(), nullable=False, server_default=""))
    op.add_column(
        "events",
        sa.Column("changes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "events",
        sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    # Remove server_default after adding column
    op.alter_column("events", "message", server_default=None)

    # Rename indexes back
    op.execute("ALTER INDEX ix_events_actor RENAME TO ix_activity_events_actor")
    op.execute("ALTER INDEX ix_events_actor_id RENAME TO ix_activity_events_actor_id")
    op.execute("ALTER INDEX ix_events_deleted_at RENAME TO ix_activity_events_deleted_at")
    op.execute("ALTER INDEX ix_events_team_created RENAME TO ix_activity_events_team_created")
    op.execute("ALTER INDEX ix_events_team_id RENAME TO ix_activity_events_team_id")
    op.execute("ALTER INDEX ix_events_team_object RENAME TO ix_activity_events_team_object")

    # Rename table back
    op.rename_table("events", "activity_events")
