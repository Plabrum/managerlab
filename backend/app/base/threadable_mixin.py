"""Mixin for models that can have threads."""

from typing import TYPE_CHECKING, Any

from sqlalchemy import and_
from sqlalchemy.orm import Mapped, declared_attr, relationship

if TYPE_CHECKING:
    from app.threads.models import Thread
    from app.threads.schemas import ThreadUnreadInfo


class ThreadableMixin:
    """Mixin for models that can have threads.

    Provides a relationship to Thread model using polymorphic association.
    The thread is identified by threadable_type (table name) and threadable_id.

    Usage:
        class Campaign(ThreadableMixin, RLSMixin(), BaseDBModel):
            __tablename__ = "campaigns"
            # ... rest of model

    The relationship can be eager-loaded:
        query = select(Campaign).options(selectinload(Campaign.thread))

    Or accessed lazily:
        campaign.thread  # Will be None if no thread exists yet
    """

    @declared_attr
    @classmethod
    def thread(cls: Any) -> Mapped["Thread | None"]:
        """Relationship to thread (if exists).

        Returns None if no thread has been created for this object yet.
        Threads are created lazily when the first message is posted.
        """
        from app.threads.models import Thread

        # Build primaryjoin using the actual model class at definition time
        # cls will be the actual model class (Campaign, Deliverable, etc.) at runtime
        tablename: str = cls.__tablename__

        return relationship(
            "Thread",
            primaryjoin=lambda: and_(
                Thread.threadable_type == tablename,
                Thread.threadable_id == cls.id,
            ),
            foreign_keys="[Thread.threadable_id]",
            viewonly=True,
            uselist=False,
            lazy="selectin",  # Automatically batch-load in queries
        )

    def get_thread_unread_info(self, user_id: int) -> "ThreadUnreadInfo | None":
        """Get ThreadUnreadInfo for this object's thread.

        This is a synchronous helper that requires the thread relationship
        to already be loaded. It computes the unread count from the loaded
        thread's messages and read_statuses.

        Args:
            user_id: User ID to calculate unread count for

        Returns:
            ThreadUnreadInfo or None if no thread exists
        """
        from app.threads.schemas import ThreadUnreadInfo

        if self.thread is None:
            return None

        # Find the user's most recent read timestamp
        last_read_at = None
        for read_status in self.thread.read_statuses:
            if read_status.user_id == user_id:
                if last_read_at is None or read_status.read_at > last_read_at:
                    last_read_at = read_status.read_at

        # Count unread messages
        unread_count = 0
        for message in self.thread.messages:
            if message.deleted_at is not None:
                continue  # Skip soft-deleted messages
            if last_read_at is None or message.created_at > last_read_at:
                unread_count += 1

        return ThreadUnreadInfo(
            thread_id=self.thread.id,
            unread_count=unread_count,
        )
