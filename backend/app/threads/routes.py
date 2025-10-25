"""Thread REST API routes."""

import logging
from typing import Annotated

from litestar import Request, Router, get, post
from litestar.params import Parameter
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.guards import requires_user_scope
from app.objects.enums import ObjectTypes
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
    notify_thread,
)
from app.utils.sqids import Sqid

logger = logging.getLogger(__name__)

# System user for messages with null user_id
ARIVE_SYSTEM_USER = UserSchema(
    id=Sqid(0),  # Special ID for system user
    email="system@arive.ai",
    name="Arive",
)


@post(
    "/{threadable_type:str}/{threadable_id:str}/messages",
)
async def create_message(
    request: Request,
    threadable_type: ObjectTypes,
    threadable_id: Sqid,
    data: MessageCreateSchema,
    transaction: AsyncSession,
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
        team_id: Team ID from session
        campaign_id: Optional campaign ID from session
        channels: Channels plugin for broadcasting

    Returns:
        Created message
    """
    # Get or create thread
    thread = await get_or_create_thread(
        transaction=transaction,
        threadable_type=threadable_type,
        threadable_id=threadable_id,
        team_id=team_id,
    )

    # Create message
    message = Message(
        thread_id=thread.id,
        user_id=request.user,
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
            "user_id": message.user_id,
            "message_id": message.id,
        },
    )

    logger.info(
        f"Created message {message.id} in thread {thread.id} "
        f"({threadable_type}:{threadable_id})"
    )

    # Load user for response
    await transaction.refresh(message, ["user"])

    # Default to Arive system user if user_id is null
    if message.user is None:
        user_schema = ARIVE_SYSTEM_USER
        user_id = Sqid(0)
    else:
        user_schema = UserSchema(
            id=message.user.id,  # Already a Sqid
            email=message.user.email,
            name=message.user.name,
        )
        user_id = message.user.id

    # Construct response
    return MessageSchema(
        id=message.id,  # Already a Sqid
        thread_id=thread.id,  # Already a Sqid
        user_id=user_id,
        content=message.content,
        created_at=message.created_at,
        updated_at=message.updated_at,
        user=user_schema,
    )


@get(
    "/{threadable_type:str}/{threadable_id:str}/messages",
)
async def list_messages(
    threadable_type: ObjectTypes,
    threadable_id: Sqid,
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
        .order_by(Message.created_at.asc())
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
    message_schemas = []
    for (message,) in rows:
        # Default to Arive system user if user_id is null
        if message.user is None:
            user_schema = ARIVE_SYSTEM_USER
            user_id = Sqid(0)
        else:
            user_schema = UserSchema(
                id=message.user.id,  # Already a Sqid
                email=message.user.email,
                name=message.user.name,
            )
            user_id = message.user.id

        message_schemas.append(
            MessageSchema(
                id=message.id,  # Already a Sqid
                thread_id=message.thread_id,  # Already a Sqid
                user_id=user_id,
                content=message.content,
                created_at=message.created_at,
                updated_at=message.updated_at,
                user=user_schema,
            )
        )

    return MessageListResponse(
        messages=message_schemas,
        offset=offset,
        limit=limit,
    )


@post("/{threadable_type:str}/batch-unread")
async def get_batch_thread_unread(
    request: Request,
    threadable_type: ObjectTypes,
    data: BatchUnreadRequest,
    transaction: AsyncSession,
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
    # object_ids are already decoded from SQID strings to ints by msgspec
    # Cast Sqid to int for function that expects list[int]
    results = await get_batch_unread_counts(
        transaction,
        threadable_type,
        [int(oid) for oid in data.object_ids],
        request.user,
    )

    # Convert to response schema
    thread_infos = []
    total_unread = 0

    for thread_id, unread_count in results:
        thread_infos.append(
            ThreadUnreadInfo(
                thread_id=Sqid(thread_id),  # Wrap int in Sqid type
                unread_count=unread_count,
            )
        )
        total_unread += unread_count

    return BatchUnreadResponse(threads=thread_infos, total_unread=total_unread)


# Router configuration
thread_router = Router(
    path="/threads",
    guards=[requires_user_scope],
    route_handlers=[
        create_message,
        list_messages,
        get_batch_thread_unread,
    ],
    tags=["threads"],
)
