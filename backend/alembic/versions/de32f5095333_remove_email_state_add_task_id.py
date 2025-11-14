"""remove_email_state_add_task_id

Revision ID: de32f5095333
Revises: 38185b743a7f
Create Date: 2025-11-13 23:33:56.526013

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from app.utils.sqids import SqidType

# revision identifiers, used by Alembic.
revision: str = "de32f5095333"
down_revision: Union[str, Sequence[str], None] = "38185b743a7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove state column and index from email_messages
    op.drop_index(op.f("ix_email_messages_state"), table_name="email_messages")
    op.drop_column("email_messages", "state")

    # Create inbound_emails table without state, with task_id
    op.create_table(
        "inbound_emails",
        sa.Column("s3_bucket", sa.Text(), nullable=False),
        sa.Column("s3_key", sa.Text(), nullable=False),
        sa.Column("from_email", sa.Text(), nullable=True),
        sa.Column("to_email", sa.Text(), nullable=True),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("ses_message_id", sa.Text(), nullable=True),
        sa.Column("received_at", sa.DateTime(), nullable=False),
        sa.Column("attachments_json", sa.JSON(), nullable=True),
        sa.Column("task_id", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("team_id", SqidType(), nullable=True),
        sa.Column("id", SqidType(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ses_message_id"),
    )
    op.create_index(op.f("ix_inbound_emails_deleted_at"), "inbound_emails", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_inbound_emails_from_email"), "inbound_emails", ["from_email"], unique=False)
    op.create_index(op.f("ix_inbound_emails_s3_key"), "inbound_emails", ["s3_key"], unique=True)
    op.create_index(op.f("ix_inbound_emails_task_id"), "inbound_emails", ["task_id"], unique=False)
    op.create_index(op.f("ix_inbound_emails_team_id"), "inbound_emails", ["team_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop inbound_emails table
    op.drop_index(op.f("ix_inbound_emails_team_id"), table_name="inbound_emails")
    op.drop_index(op.f("ix_inbound_emails_task_id"), table_name="inbound_emails")
    op.drop_index(op.f("ix_inbound_emails_s3_key"), table_name="inbound_emails")
    op.drop_index(op.f("ix_inbound_emails_from_email"), table_name="inbound_emails")
    op.drop_index(op.f("ix_inbound_emails_deleted_at"), table_name="inbound_emails")
    op.drop_table("inbound_emails")

    # Re-add state column and index to email_messages
    op.add_column("email_messages", sa.Column("state", sa.Text(), server_default="PENDING", nullable=False))
    op.create_index(op.f("ix_email_messages_state"), "email_messages", ["state"], unique=False)
