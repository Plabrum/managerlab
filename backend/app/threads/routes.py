"""Thread REST API routes."""

import logging
from typing import Annotated

from litestar import Router, get, post
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.guards import requires_user_scope
from app.threads.models import Thread, Message
from app.threads.schemas import (
    MessageSchema,
    UserSchema,
    MessageCreateSchema,
    MessageListResponse,
    BatchUnreadRequest,
    BatchUnreadResponse,
    ThreadUnreadInfo,
)
from app.threads.services import (
    get_or_create_thread,
    get_batch_unread_counts,
    mark_thread_as_read,
    notify_thread,
)
from app.utils.sqids import sqid_decode, sqid_encode

logger = logging.getLogger(__name__)


@post(
    "/{threadable_type:str}/{threadable_id:int}/messages",
)
async def create_message(
    threadable_type: str,
    threadable_id: int,
    data: MessageCreateSchema,
    transaction: AsyncSession,
    user_id: int,
    team_id: int,
    campaign_id: int | None,
) -> MessageSchema:
    """Create a new message in a thread.

    Auto-creates the thread if it doesn't exist.
    Broadcasts a notification to WebSocket subscribers.

    Args:
        threadable_type: Type of object (e.g., "DeliverableMedia")
        threadable_id: ID of the object
        data: Message content
        transaction: Database session
        user_id: Authenticated user ID
        team_id: Team ID from session
        campaign_id: Optional campaign ID from session
        channels: Channels plugin for broadcasting

    Returns:
        Created message
    """
    # Get or create thread
    thread = await get_or_create_thread(
        transaction,
        threadable_type,
        threadable_id,
        team_id,
        campaign_id,
    )

    # Create message
    message = Message(
        thread_id=thread.id,
        user_id=user_id,
        content=data.content,
        team_id=team_id,
        campaign_id=campaign_id,
    )
    transaction.add(message)
    await transaction.flush()

    # Notify WebSocket subscribers via PostgreSQL NOTIFY
    await notify_thread(
        transaction,
        thread.id,
        {
            "type": "new_message",
            "thread_id": thread.id,
            "user_id": user_id,
        },
    )

    logger.info(
        f"Created message {message.id} in thread {thread.id} "
        f"({threadable_type}:{threadable_id})"
    )

    # Load user for response
    await transaction.refresh(message, ["user"])

    # Construct response
    return MessageSchema(
        id=message.public_id,
        thread_id=thread.public_id,
        user_id=message.user.public_id,
        content=message.content,
        created_at=message.created_at,
        updated_at=message.updated_at,
        user=UserSchema(
            id=message.user.public_id,
            email=message.user.email,
            name=message.user.name,
        ),
    )


@get(
    "/{threadable_type:str}/{threadable_id:int}/messages",
)
async def list_messages(
    threadable_type: str,
    threadable_id: int,
    transaction: AsyncSession,
    offset: Annotated[int, Parameter(ge=0)] = 0,
    limit: Annotated[int, Parameter(ge=1, le=100)] = 50,
) -> MessageListResponse:
    """List messages in a thread with pagination.

    Returns the most recent messages, ordered by creation time descending.
    Excludes soft-deleted messages.

    Args:
        threadable_type: Type of object
        threadable_id: ID of the object
        transaction: Database session
        offset: Pagination offset
        limit: Number of messages to return (max 100)

    Returns:
        Paginated list of messages
    """
    # Single query joining Thread and Message
    stmt = (
        select(Message)
        .join(
            Thread,
            and_(
                Message.thread_id == Thread.id,
                Thread.threadable_type == threadable_type,
                Thread.threadable_id == threadable_id,
            ),
        )
        .where(Message.deleted_at.is_(None))
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(limit)
        .options(selectinload(Message.user))
    )

    result = await transaction.execute(stmt)
    rows = result.all()

    if not rows:
        # No messages found
        return MessageListResponse(
            messages=[],
            offset=offset,
            limit=limit,
        )

    # Convert to schemas
    message_schemas = [
        MessageSchema(
            id=message.public_id,
            thread_id=thread.public_id,
            user_id=message.user.public_id,
            content=message.content,
            created_at=message.created_at,
            updated_at=message.updated_at,
            user=UserSchema(
                id=message.user.public_id,
                email=message.user.email,
                name=message.user.name,
            ),
        )
        for message, thread in rows
    ]

    return MessageListResponse(
        messages=message_schemas,
        offset=offset,
        limit=limit,
    )


@post("/{threadable_type:str}/batch-unread")
async def get_batch_thread_unread(
    threadable_type: str,
    data: BatchUnreadRequest,
    transaction: AsyncSession,
    user_id: int,
) -> BatchUnreadResponse:
    """Get unread counts for multiple threads in a single request.

    This is much more efficient than calling the single unread endpoint
    multiple times when displaying a list of objects with unread badges.

    Args:
        threadable_type: Type of object (e.g., "DeliverableMedia")
        data: List of object IDs to check
        transaction: Database session
        user_id: Authenticated user ID

    Returns:
        Unread counts for each requested object and total unread count
    """
    if not data.object_ids:
        return BatchUnreadResponse(threads=[], total_unread=0)

    # Get unread counts for all requested threads
    results = await get_batch_unread_counts(
        transaction,
        threadable_type,
        [sqid_decode(o) for o in data.object_ids],
        user_id,
    )

    # Convert to response schema
    thread_infos = []
    total_unread = 0

    for thread_id, unread_count in results:
        thread_infos.append(
            ThreadUnreadInfo(
                thread_id=sqid_encode(thread_id),
                unread_count=unread_count,
            )
        )
        total_unread += unread_count

    return BatchUnreadResponse(threads=thread_infos, total_unread=total_unread)


@post(
    "/{threadable_type:str}/{threadable_id:int}/mark-read",
    status_code=204,
)
async def mark_thread_read(
    threadable_type: str,
    threadable_id: int,
    transaction: AsyncSession,
    user_id: int,
) -> None:
    """Mark all messages in a thread as read for the current user.

    Updates or creates the read status with the current timestamp.

    Args:
        threadable_type: Type of object
        threadable_id: ID of the object
        transaction: Database session
        user_id: Authenticated user ID

    Raises:
        NotFoundException: If thread not found
    """
    # Find the thread
    stmt = select(Thread).where(
        Thread.threadable_type == threadable_type,
        Thread.threadable_id == threadable_id,
    )
    result = await transaction.execute(stmt)
    thread = result.scalar_one_or_none()

    if not thread:
        raise NotFoundException(detail="Thread not found")

    # Mark as read
    await mark_thread_as_read(transaction, thread.id, user_id)


# Router configuration
thread_router = Router(
    path="/threads",
    guards=[requires_user_scope],
    route_handlers=[
        create_message,
        list_messages,
        get_batch_thread_unread,
        mark_thread_read,
    ],
    tags=["threads"],
)
