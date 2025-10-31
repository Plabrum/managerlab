"""fix deliverable_media use id as primary key

Revision ID: e8da4b2f4c09
Revises: 31e0afb7f242
Create Date: 2025-10-22 13:16:01.016752

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8da4b2f4c09"
down_revision: str | Sequence[str] | None = "31e0afb7f242"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing table (safe because production is empty)
    op.drop_table("deliverable_media")

    # Recreate with correct schema - id as primary key
    op.create_table(
        "deliverable_media",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("deliverable_id", sa.Integer(), nullable=False),
        sa.Column("media_id", sa.Integer(), nullable=False),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("is_featured", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["deliverable_id"], ["deliverables.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["media_id"], ["media.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_deliverable_media_deleted_at"), "deliverable_media", ["deleted_at"])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the table
    op.drop_index(op.f("ix_deliverable_media_deleted_at"), "deliverable_media")
    op.drop_table("deliverable_media")

    # Recreate with old composite primary key schema
    op.create_table(
        "deliverable_media",
        sa.Column("deliverable_id", sa.Integer(), nullable=False),
        sa.Column("media_id", sa.Integer(), nullable=False),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("is_featured", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["deliverable_id"], ["deliverables.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["media_id"], ["media.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("deliverable_id", "media_id"),
    )
    op.create_index(op.f("ix_deliverable_media_deleted_at"), "deliverable_media", ["deleted_at"])
