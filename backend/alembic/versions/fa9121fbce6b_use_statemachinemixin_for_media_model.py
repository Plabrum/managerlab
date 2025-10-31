"""Use StateMachineMixin for Media model

Revision ID: fa9121fbce6b
Revises: 06ea3c9fc6cd
Create Date: 2025-10-12 23:07:38.125591

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fa9121fbce6b"
down_revision: str | Sequence[str] | None = "06ea3c9fc6cd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename media.status column to media.state
    op.alter_column("media", "status", new_column_name="state")

    # Add index on state column for StateMachineMixin
    op.create_index(op.f("ix_media_state"), "media", ["state"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove index on state column
    op.drop_index(op.f("ix_media_state"), table_name="media")

    # Rename media.state column back to media.status
    op.alter_column("media", "state", new_column_name="status")
