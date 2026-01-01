import logging
from datetime import UTC, datetime
from typing import cast

from litestar.channels import ChannelsPlugin
from litestar.stores.base import Store
from litestar.stores.memory import MemoryStore
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.threads.models import Message, Thread, ThreadReadStatus
from app.threads.schemas import (
    ServerMessage,
)
from app.threads.utils import encode_server_message_str, get_thread_channel
from app.utils.tracing import trace_operation

logger = logging.getLogger(__name__)


# ============================================================================
# WebSocket Viewer Presence Management (In-Memory with MemoryStore)
# ============================================================================


class ThreadViewerStore:
    def __init__(self, store: Store):
        # N.B. When switching to use a redis backed store, we will have to handle serialization here
        self.store: MemoryStore = cast(MemoryStore, store)

    def get_key(self, thread_id: int) -> str:
        return f"thread_id_{thread_id}"

    async def get_viewers(self, thread_id: int) -> set[int]:
        data = await self.store.get(self.get_key(thread_id))
        return cast(set[int], data) if data else set()

    async def add_viewer(self, thread_id: int, user_id: int) -> set[int]:
        viewers = await self.get_viewers(thread_id)
        viewers.add(user_id)
        await self.store.set(self.get_key(thread_id), cast(bytes, viewers))
        return viewers

    async def remove_viewer(self, thread_id: int, user_id: int) -> set[int]:
        viewers = await self.get_viewers(thread_id)
        viewers.discard(user_id)
        await self.store.set(self.get_key(thread_id), cast(bytes, viewers))
        return viewers


@trace_operation("get_or_create_thread")
async def get_or_create_thread(
    transaction: AsyncSession,
    threadable_type: str,
    threadable_id: int,
    team_id: int,
) -> Thread:
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


@trace_operation("send_thread_notification")
async def notify_thread(
    channels: ChannelsPlugin,
    thread_id: int,
    message: ServerMessage,
) -> None:
    try:
        channels.publish(
            encode_server_message_str(message),
            [get_thread_channel(thread_id)],
        )
        logger.debug(f"Notified thread {thread_id}: {message}")
    except Exception as e:
        logger.warning(f"Failed to notify thread {thread_id}: {e}")
