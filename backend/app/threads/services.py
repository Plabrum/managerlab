"""Thread service layer for business logic and WebSocket management."""

import logging
from datetime import datetime, timezone

from litestar.channels import ChannelsPlugin
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.threads.models import Thread, Message, ThreadReadStatus, ThreadViewerEvent
from app.threads.websocket_messages import (
    ViewerInfo,
    ServerMessage,
    encode_server_message_str,
)

logger = logging.getLogger(__name__)


# ============================================================================
# WebSocket Viewer Presence Management (DB-backed, multi-server safe)
# ============================================================================


async def get_current_viewers_from_db(
    session: AsyncSession, thread_id: int
) -> list[ViewerInfo]:
    """Get current viewers for a thread by querying the event log.

    Reconstructs current viewer state from append-only event log.
    A user is "currently viewing" if their last event was "joined".

    Args:
        session: Database session
        thread_id: Thread ID

    Returns:
        List of current viewers with typing status (always False on initial load)
    """
    # Subquery: Get most recent event for each user in this thread
    latest_event_subq = (
        select(
            ThreadViewerEvent.user_id,
            func.max(ThreadViewerEvent.created_at).label("latest_created_at"),
        )
        .where(ThreadViewerEvent.thread_id == thread_id)
        .group_by(ThreadViewerEvent.user_id)
        .subquery()
    )

    # Get the actual latest events for each user
    stmt = (
        select(ThreadViewerEvent)
        .join(
            latest_event_subq,
            (ThreadViewerEvent.user_id == latest_event_subq.c.user_id)
            & (ThreadViewerEvent.created_at == latest_event_subq.c.latest_created_at),
        )
        .where(
            ThreadViewerEvent.thread_id == thread_id,
            ThreadViewerEvent.event_type
            == "joined",  # Only users whose last event was "joined"
        )
    )

    result = await session.execute(stmt)
    events = result.scalars().all()

    return [
        ViewerInfo(
            user_id=event.user_id,
            name=event.user_name,
            is_typing=False,  # Typing status is ephemeral, always starts as False
        )
        for event in events
    ]


async def record_viewer_joined(
    session: AsyncSession, thread_id: int, user_id: int, user_name: str
) -> None:
    """Record a viewer joined event in the database.

    Args:
        session: Database session
        thread_id: Thread ID
        user_id: User ID
        user_name: User's display name
    """
    event = ThreadViewerEvent(
        thread_id=thread_id,
        user_id=user_id,
        event_type="joined",
        user_name=user_name,
    )
    session.add(event)
    await session.flush()

    logger.debug(f"User {user_id} joined thread {thread_id} (recorded to DB)")


async def record_viewer_left(
    session: AsyncSession, thread_id: int, user_id: int
) -> None:
    """Record a viewer left event in the database.

    Args:
        session: Database session
        thread_id: Thread ID
        user_id: User ID
    """
    # Get user name from most recent joined event (needed for denormalization)
    stmt = (
        select(ThreadViewerEvent.user_name)
        .where(
            ThreadViewerEvent.thread_id == thread_id,
            ThreadViewerEvent.user_id == user_id,
            ThreadViewerEvent.event_type == "joined",
        )
        .order_by(ThreadViewerEvent.created_at.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    user_name = result.scalar_one_or_none()

    if not user_name:
        logger.warning(
            f"Could not find user name for viewer {user_id} in thread {thread_id}"
        )
        user_name = "Unknown"

    event = ThreadViewerEvent(
        thread_id=thread_id,
        user_id=user_id,
        event_type="left",
        user_name=user_name,
    )
    session.add(event)
    await session.flush()

    logger.debug(f"User {user_id} left thread {thread_id} (recorded to DB)")


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

    logger.info(
        f"Created new thread for {threadable_type}:{threadable_id} (thread_id={thread.id})"
    )

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
                (max_read_subq.c.last_read_at.is_(None))
                | (Message.created_at > max_read_subq.c.last_read_at)
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
    now = datetime.now(tz=timezone.utc)

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
    channels: ChannelsPlugin,
    thread_id: int,
    message: ServerMessage,
    viewers: list[ViewerInfo],
) -> None:
    """Broadcast a message to a thread via Channels plugin.

    Args:
        channels: ChannelsPlugin instance from DI
        thread_id: Thread ID to notify
        message: Typed server message to broadcast (without viewers field)
        viewers: Current viewers list to include in message
    """
    # Add viewers to message using msgspec struct manipulation
    # Since structs are frozen, we need to recreate with viewers
    from app.threads.websocket_messages import (
        MessageUpdateMessage,
        UserJoinedMessage,
        UserLeftMessage,
        TypingUpdateMessage,
        MarkedReadMessage,
    )

    # Match on message type and add viewers field
    if isinstance(message, MessageUpdateMessage):
        message_with_viewers = MessageUpdateMessage(
            update_type=message.update_type,
            message_id=message.message_id,
            thread_id=message.thread_id,
            user_id=message.user_id,
            viewers=viewers,
        )
    elif isinstance(message, UserJoinedMessage):
        message_with_viewers = UserJoinedMessage(
            user_id=message.user_id, viewers=viewers
        )
    elif isinstance(message, UserLeftMessage):
        message_with_viewers = UserLeftMessage(user_id=message.user_id, viewers=viewers)
    elif isinstance(message, TypingUpdateMessage):
        message_with_viewers = TypingUpdateMessage(
            user_id=message.user_id, is_typing=message.is_typing, viewers=viewers
        )
    elif isinstance(message, MarkedReadMessage):
        message_with_viewers = MarkedReadMessage(viewers=viewers)
    else:
        # Fallback - shouldn't happen with typed unions
        logger.error(f"Unknown message type: {type(message)}")
        return

    channel = f"thread_{thread_id}"
    payload = encode_server_message_str(message_with_viewers)

    channels.publish(payload, [channel])

    logger.debug(f"Notified thread {thread_id}: {message}")
