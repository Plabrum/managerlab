"""Thread REST API routes."""

import logging
from typing import Annotated

from litestar import Request, Router, get, post
from litestar.channels import ChannelsPlugin
from litestar.params import Parameter
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.guards import requires_user_scope
from app.objects.enums import ObjectTypes
from app.threads.enums import ThreadSocketMessageType
from app.threads.models import Message, Thread
from app.threads.schemas import (
    BatchUnreadRequest,
    BatchUnreadResponse,
    MessageCreateSchema,
    MessageListResponse,
    MessageSchema,
    MessageSenderSchema,
    ServerMessage,
    ThreadUnreadInfo,
)
from app.threads.services import (
    get_batch_unread_counts,
    get_or_create_thread,
    notify_thread,
)
from app.users.models import User
from app.utils.db import get_or_404
from app.utils.sqids import Sqid, sqid_encode

logger = logging.getLogger(__name__)

# System user for messages with null user_id
ARIVE_SYSTEM_USER = MessageSenderSchema(
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
    channels: ChannelsPlugin,
) -> MessageSchema:
    user = await get_or_404(transaction, User, request.user)
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
        user_id=user.id,
        content=data.content,
        team_id=team_id,
        campaign_id=campaign_id,
    )
    transaction.add(message)
    await transaction.flush()

    # Notify WebSocket subscribers via Channels
    await notify_thread(
        channels,
        thread.id,
        ServerMessage(
            message_type=ThreadSocketMessageType.MESSAGE_CREATED,
            message_id=sqid_encode(message.id),
            thread_id=sqid_encode(thread.id),
            user_id=sqid_encode(user.id),
            viewers=[],  # Empty - REST routes don't have viewer_store access
        ),
    )

    logger.info(f"Created message {message.id} in thread {thread.id} ({threadable_type}:{threadable_id})")

    user_schema = MessageSenderSchema(
        id=user.id,  # Already a Sqid
        email=user.email,
        name=user.name,
    )

    # Construct response
    return MessageSchema(
        id=message.id,
        thread_id=thread.id,
        user_id=user.id,
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
        .options(joinedload(Message.user), joinedload(Message.thread))
    )

    result = await transaction.execute(stmt)
    rows = result.scalars()

    if not rows:
        # No messages found
        return MessageListResponse(
            messages=[],
            offset=offset,
            limit=limit,
        )

    # Convert to schemas
    message_schemas = []
    for message in rows:
        # Default to Arive system user if user_id is null
        if message.user is None:
            user_schema = ARIVE_SYSTEM_USER
            user_id = Sqid(0)
        else:
            user_schema = MessageSenderSchema(
                id=message.user.id,  # Already a Sqid
                email=message.user.email,
                name=message.user.name,
            )
            user_id = message.user.id

        message_schemas.append(
            MessageSchema(
                id=message.id,  # Already a Sqid
                thread_id=message.thread.id,  # Already a Sqid
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
