"""Thread models for threads and messages."""

from datetime import datetime
from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin

if TYPE_CHECKING:
    from app.users.models import User


class Thread(
    RLSMixin(),
    BaseDBModel,
):
    """Thread model for polymorphic threads.

    Any object can have a thread by storing its type and ID.
    For example: DeliverableMedia, Campaign, Invoice, etc.
    """

    __tablename__ = "threads"

    # Polymorphic association
    threadable_type: Mapped[str] = mapped_column(sa.Text, nullable=False, index=True)
    threadable_id: Mapped[int] = mapped_column(sa.Integer, nullable=False, index=True)

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    read_statuses: Mapped[list["ThreadReadStatus"]] = relationship(
        "ThreadReadStatus",
        back_populates="thread",
        cascade="all, delete-orphan",
    )

    # Unique constraint: only one thread per object
    __table_args__ = (
        sa.UniqueConstraint(
            "threadable_type",
            "threadable_id",
            name="uq_thread_per_object",
        ),
    )


class Message(
    RLSMixin(scope_with_campaign_id=True),
    BaseDBModel,
):
    """Message model for messages within threads."""

    __tablename__ = "messages"

    # Foreign keys
    thread_id: Mapped[int] = mapped_column(
        sa.ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Content
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # Relationships
    thread: Mapped["Thread"] = relationship("Thread", back_populates="messages")
    user: Mapped["User"] = relationship("User")

    # Index for efficient message listing
    __table_args__ = (
        sa.Index("ix_messages_thread_created", "thread_id", "created_at"),
    )


class ThreadReadStatus(BaseDBModel):
    """Log of thread read events.

    Append-only log used to calculate unread message counts.
    Each time a user marks a thread as read, a new row is inserted.
    """

    __tablename__ = "thread_read_statuses"

    # Foreign keys
    thread_id: Mapped[int] = mapped_column(
        sa.ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Read timestamp
    read_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    thread: Mapped["Thread"] = relationship("Thread", back_populates="read_statuses")
    user: Mapped["User"] = relationship("User")

    # Index for efficient MAX(read_at) lookups
    __table_args__ = (
        sa.Index(
            "ix_thread_read_status_lookup",
            "thread_id",
            "user_id",
            "read_at",
        ),
    )
