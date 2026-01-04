"""Email message models."""

from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.utils.sqids import Sqid


class EmailMessage(
    RLSMixin(),
    BaseDBModel,
):
    """Outbound email messages."""

    __tablename__ = "email_messages"

    # Recipients
    to_email: Mapped[str] = mapped_column(sa.Text, nullable=False)
    from_email: Mapped[str] = mapped_column(sa.Text, nullable=False)
    reply_to_email: Mapped[str | None] = mapped_column(sa.Text)

    # Content
    subject: Mapped[str] = mapped_column(sa.Text, nullable=False)
    body_html: Mapped[str] = mapped_column(sa.Text, nullable=False)
    body_text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # SES tracking
    ses_message_id: Mapped[str | None] = mapped_column(sa.Text, unique=True)
    sent_at: Mapped[datetime | None]

    # Metadata
    template_name: Mapped[str | None] = mapped_column(sa.Text)

    def __repr__(self) -> str:
        return f"<EmailMessage(id={self.id}, to={self.to_email}, subject={self.subject[:30]})>"


class InboundEmail(BaseDBModel):
    """Inbound emails received via SES."""

    __tablename__ = "inbound_emails"

    # S3 storage (required immediately, populated by webhook)
    s3_bucket: Mapped[str] = mapped_column(sa.Text, nullable=False)
    s3_key: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True, index=True)

    # Email metadata (parsed from S3 by task)
    from_email: Mapped[str] = mapped_column(sa.Text, nullable=False, index=True)
    to_email: Mapped[str | None] = mapped_column(sa.Text)
    subject: Mapped[str | None] = mapped_column(sa.Text)
    ses_message_id: Mapped[str | None] = mapped_column(sa.Text, unique=True)
    received_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    # Attachment metadata (JSONB array of attachment info)
    attachments_json: Mapped[dict] = mapped_column(
        postgresql.JSONB,
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    # Processing status
    task_id: Mapped[str | None] = mapped_column(sa.Text, index=True)
    processed_at: Mapped[datetime | None]

    # Team linking (determined from sender's primary_team)
    team_id: Mapped[Sqid] = mapped_column(
        sa.ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        subj = self.subject[:30] if self.subject else "no subject"
        return f"<InboundEmail(id={self.id}, from={self.from_email}, subject={subj})>"
