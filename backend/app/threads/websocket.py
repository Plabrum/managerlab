"""WebSocket handler for real-time thread updates using Litestar Channels plugin."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from litestar import WebSocket
from litestar.channels import ChannelsPlugin
from litestar.exceptions import WebSocketDisconnect
from litestar.handlers import websocket_listener
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guards import requires_user_scope
from app.objects.enums import ObjectTypes
from app.threads.models import Thread
from app.threads.services import (
    get_current_viewers_from_db,
    mark_thread_as_read,
    record_viewer_joined,
    record_viewer_left,
)
from app.threads.websocket_messages import (
    ClientMessage,
    MarkedReadMessage,
    MarkReadMessage,
    ServerMessage,
    TypingMessage,
    TypingUpdateMessage,
    UserJoinedMessage,
    UserLeftMessage,
    ViewerInfo,
    encode_server_message_str,  # Only needed for channels.publish()
)
from app.users.models import User
from app.utils.sqids import Sqid

logger = logging.getLogger(__name__)


# ============================================================================
# Message Handlers
# ============================================================================


async def handle_typing_message(
    message: TypingMessage,
    thread_id: int,
    user_id: int,
    channels: ChannelsPlugin,
    transaction: AsyncSession,
) -> None:
    """Handle typing indicator updates from clients."""
    # Get current viewers from DB
    viewers = await get_current_viewers_from_db(transaction, thread_id)

    # Update typing status for current user
    updated_viewers = [
        ViewerInfo(
            user_id=viewer.user_id,
            name=viewer.name,
            is_typing=message.is_typing
            if viewer.user_id == user_id
            else viewer.is_typing,
        )
        for viewer in viewers
    ]

    # Broadcast typing update to all viewers
    typing_update = TypingUpdateMessage(
        user_id=user_id, is_typing=message.is_typing, viewers=updated_viewers
    )
    # Note: channels.publish() needs manual encoding (not a handler return)
    channels.publish(encode_server_message_str(typing_update), [f"thread_{thread_id}"])


async def handle_mark_read_message(
    message: MarkReadMessage,
    thread_id: int,
    user_id: int,
    transaction: AsyncSession,
) -> MarkedReadMessage:
    """Handle mark-as-read requests from clients."""
    # Mark thread as read
    await mark_thread_as_read(transaction, thread_id, user_id)
    await transaction.commit()

    # Get current viewers from DB
    viewers = await get_current_viewers_from_db(transaction, thread_id)

    # Return confirmation to sender
    return MarkedReadMessage(viewers=viewers)


# ============================================================================
# WebSocket Lifecycle & Handler
# ============================================================================


@asynccontextmanager
async def thread_connection_lifespan(
    socket: WebSocket,
    channels: ChannelsPlugin,
    threadable_type: ObjectTypes,
    threadable_id: Sqid,
    transaction: AsyncSession,
) -> AsyncGenerator[None, None]:
    """Manage WebSocket connection lifecycle for thread notifications."""
    # Find thread (RLS will enforce access)
    stmt = select(Thread).where(
        Thread.threadable_type == threadable_type,
        Thread.threadable_id == threadable_id,
    )
    result = await transaction.execute(stmt)
    thread = result.scalar_one_or_none()

    if not thread:
        await socket.close(code=1008, reason="Thread not found")
        return

    thread_id = thread.id
    user_id = socket.user

    # Load user name from database
    user_stmt = select(User).where(User.id == user_id)
    user_result = await transaction.execute(user_stmt)
    user = user_result.scalar_one()
    user_name = user.name

    # Get current viewers from DB
    viewers = await get_current_viewers_from_db(transaction, thread_id)

    # Add this user to viewers list
    viewers.append(ViewerInfo(user_id=user_id, name=user_name, is_typing=False))

    # Record joined event in DB
    await record_viewer_joined(transaction, thread_id, user_id, user_name)
    await transaction.commit()

    # Notify other users that someone joined
    join_message = UserJoinedMessage(user_id=user_id, viewers=viewers)
    channels.publish(encode_server_message_str(join_message), [f"thread_{thread_id}"])

    logger.info(
        f"WebSocket connected: user {user_id} ({user_name}) -> thread {thread_id}"
    )

    # Subscribe to channel and run background sender
    channel_name = f"thread_{thread_id}"

    async with channels.start_subscription([channel_name]) as subscriber:
        try:
            # Background task sends all incoming messages to WebSocket
            async with subscriber.run_in_background(socket.send_text):
                # Store connection state for handler
                socket.state["thread_id"] = thread_id
                socket.state["user_id"] = user_id
                socket.state["user_name"] = user_name
                yield
        except WebSocketDisconnect:
            pass
        finally:
            # User disconnected - clean up
            # Create new session for cleanup (old one may be closed)
            from sqlalchemy.ext.asyncio import (
                AsyncSession as AsyncSessionClass,
                AsyncEngine,
            )

            engine = transaction.get_bind()
            # Type assertion - get_bind returns Engine | Connection, but we know it's an AsyncEngine
            assert isinstance(engine, AsyncEngine)
            async with AsyncSessionClass(
                engine, expire_on_commit=False
            ) as cleanup_session:
                # Record viewer left event in DB
                await record_viewer_left(cleanup_session, thread_id, user_id)
                await cleanup_session.commit()

                # Get updated viewers list
                updated_viewers = await get_current_viewers_from_db(
                    cleanup_session, thread_id
                )

                # Notify other users that someone left
                left_message = UserLeftMessage(user_id=user_id, viewers=updated_viewers)
                channels.publish(
                    encode_server_message_str(left_message), [f"thread_{thread_id}"]
                )

            logger.info(
                f"WebSocket disconnected: user {user_id} from thread {thread_id}"
            )


@websocket_listener(
    "/ws/threads/{threadable_type:str}/{threadable_id:str}",
    connection_lifespan=thread_connection_lifespan,
    guards=[requires_user_scope],
)
async def thread_handler(
    data: ClientMessage,
    channels: ChannelsPlugin,
    socket: WebSocket,
    transaction: AsyncSession,
) -> ServerMessage | None:
    """Handle incoming client messages (typing indicators and mark-read requests)."""
    # Get connection state
    thread_id: int = socket.state["thread_id"]
    user_id: int = socket.state["user_id"]

    # Route to appropriate handler based on message type
    match data:
        case TypingMessage():
            await handle_typing_message(data, thread_id, user_id, channels, transaction)
            return None  # Don't send response back to sender

        case MarkReadMessage():
            return await handle_mark_read_message(data, thread_id, user_id, transaction)
