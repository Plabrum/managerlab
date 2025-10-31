"""Thread service layer for business logic and WebSocket management."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.threads.models import Message, Thread, ThreadReadStatus

logger = logging.getLogger(__name__)


async def get_or_create_thread(
    transaction: AsyncSession,
    threadable_type: str,
    threadable_id: int,
    team_id: int,
) -> Thread:
    """Get existing thread or create a new one for the given object.

    Args:
        session: Database session
        threadable_type: Type of object (e.g., "DeliverableMedia", "Campaign")
        threadable_id: ID of the object
        team_id: Team ID for RLS scoping
        campaign_id: Optional campaign ID for dual-scoped objects

    Returns:
        Thread instance (existing or newly created)
    """
    # Try to find existing thread
    stmt = select(Thread).where(
        Thread.threadable_type == threadable_type,
        Thread.threadable_id == threadable_id,
    )
    result = await transaction.execute(stmt)
    thread = result.scalar_one_or_none()

    if thread:
        return thread

    # Create new thread
    thread = Thread(
        threadable_type=threadable_type,
        threadable_id=threadable_id,
        team_id=team_id,
    )
    transaction.add(thread)
    await transaction.flush()

    logger.info(f"Created new thread for {threadable_type}:{threadable_id} (thread_id={thread.id})")

    return thread


async def get_unread_count(
    session: AsyncSession,
    thread_id: int,
    user_id: int,
) -> int:
    """Calculate unread message count for a user in a thread.

    Messages are unread if they were created after the user's last read_at timestamp.
    If user has never read the thread, all non-deleted messages are unread.

    Args:
        session: Database session
        thread_id: Thread ID
        user_id: User ID

    Returns:
        Count of unread messages
    """
    # Get user's most recent read timestamp
    last_read_stmt = select(func.max(ThreadReadStatus.read_at)).where(
        ThreadReadStatus.thread_id == thread_id,
        ThreadReadStatus.user_id == user_id,
    )
    result = await session.execute(last_read_stmt)
    last_read_at = result.scalar_one_or_none()

    # Build query for unread messages
    query = (
        select(func.count())
        .select_from(Message)
        .where(
            Message.thread_id == thread_id,
            Message.deleted_at.is_(None),  # Exclude soft-deleted messages
        )
    )

    if last_read_at:
        # Count messages created after last read
        query = query.where(Message.created_at > last_read_at)
    # else: all messages are unread (user has never read this thread)

    result = await session.execute(query)
    count = result.scalar_one()

    return count


async def get_batch_unread_counts(
    session: AsyncSession,
    threadable_type: str,
    threadable_ids: list[int],
    user_id: int,
) -> list[tuple[int, int]]:
    """Get unread counts for multiple threads efficiently.

    Args:
        session: Database session
        threadable_type: Type of object (e.g., "DeliverableMedia")
        threadable_ids: List of object IDs
        user_id: User ID

    Returns:
        Dict mapping threadable_id -> (thread_id, unread_count)
        Returns (None, 0) for objects without threads
    """
    # Subquery to get MAX(read_at) per thread for this user
    max_read_subq = (
        select(
            ThreadReadStatus.thread_id,
            func.max(ThreadReadStatus.read_at).label("last_read_at"),
        )
        .where(ThreadReadStatus.user_id == user_id)
        .group_by(ThreadReadStatus.thread_id)
        .subquery()
    )

    # Single query to get all thread info and unread counts
    # Left join max_read_subq to get last_read_at for each thread
    # Count messages where created_at > last_read_at (or all messages if never read)
    stmt = (
        select(
            Thread.id.label("thread_id"),
            max_read_subq.c.last_read_at,
            func.count(Message.id).label("unread_count"),
        )
        .select_from(Thread)
        .outerjoin(max_read_subq, max_read_subq.c.thread_id == Thread.id)
        .outerjoin(
            Message,
            (Message.thread_id == Thread.id)
            & (Message.deleted_at.is_(None))
            & (
                # Message is unread if created after last_read_at OR never read
                (max_read_subq.c.last_read_at.is_(None)) | (Message.created_at > max_read_subq.c.last_read_at)
            ),
        )
        .where(
            Thread.threadable_type == threadable_type,
            Thread.threadable_id.in_(threadable_ids),
        )
        .group_by(Thread.id, max_read_subq.c.last_read_at)
    )

    result = await session.execute(stmt)
    rows = result.all()
    return [(row.thread_id, row.unread_count) for row in rows]


async def mark_thread_as_read(
    session: AsyncSession,
    thread_id: int,
    user_id: int,
) -> None:
    """Mark all messages in a thread as read for a user.

    Appends a new read event to the log.

    Args:
        session: Database session
        thread_id: Thread ID
        user_id: User ID
    """
    now = datetime.now(tz=UTC)

    # Simple INSERT - append-only log
    read_status = ThreadReadStatus(
        thread_id=thread_id,
        user_id=user_id,
        read_at=now,
    )
    session.add(read_status)
    await session.flush()

    logger.info(f"Marked thread {thread_id} as read for user {user_id}")


async def notify_thread(
    session: AsyncSession,
    thread_id: int,
    message: dict[str, Any],
) -> None:
    """Broadcast a message to a thread via PostgreSQL NOTIFY.

    Args:
        session: Database session
        thread_id: Thread ID to notify
        message: Message payload (will be JSON-encoded)
    """
    channel = f"thread_{thread_id}"
    payload = json.dumps(message)

    # PostgreSQL NOTIFY doesn't support parameterized queries
    # Use dollar-quoted strings to avoid escaping issues
    await session.execute(text(f"NOTIFY {channel}, $${payload}$$"))

    logger.debug(f"Notified thread {thread_id}: {message.get('type')}")
