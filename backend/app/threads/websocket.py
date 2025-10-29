"""WebSocket handler for real-time thread updates using Litestar Channels plugin."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from litestar import WebSocket
from litestar.channels import ChannelsPlugin
from litestar.exceptions import WebSocketDisconnect
from litestar.handlers import websocket_listener
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guards import requires_user_scope
from app.objects.enums import ObjectTypes
from app.threads.services import (
    ThreadViewerStore,
    get_or_create_thread,
    mark_thread_as_read,
)
from app.threads.utils import encode_server_message_str, get_thread_channel
from app.threads.schemas import (
    ClientMessage,
    MarkReadMessage,
    ServerMessage,
    TypingMessage,
    TypingUpdateMessage,
    UserJoinedMessage,
    UserLeftMessage,
)
from app.utils.sqids import Sqid, sqid_encode

logger = logging.getLogger(__name__)


# ============================================================================
# Message Handlers
# ============================================================================


async def handle_typing_message(
    message: TypingMessage,
    thread_id: int,
    user_id: int,
    channels: ChannelsPlugin,
    viewer_store: ThreadViewerStore,
) -> None:
    """Handle typing indicator updates from clients.

    Typing messages act as a heartbeat to ensure the user is tracked as a viewer.
    """
    # Ensure user is tracked as a viewer (heartbeat)
    viewer_ids = await viewer_store.add_viewer(thread_id, user_id)

    typing_update = TypingUpdateMessage(
        user_id=sqid_encode(user_id),
        is_typing=message.is_typing,
        viewers=[sqid_encode(viewer) for viewer in viewer_ids],
    )
    # Note: channels.publish() needs manual encoding (not a handler return)
    channels.publish(
        encode_server_message_str(typing_update), [get_thread_channel(thread_id)]
    )


async def handle_mark_read_message(
    thread_id: int,
    user_id: int,
    transaction: AsyncSession,
) -> None:
    """Handle mark-as-read requests from clients."""
    # Mark thread as read
    await mark_thread_as_read(transaction, thread_id, user_id)
    await transaction.commit()
    return None


async def handle_user_joined(
    thread_id: int,
    user_id: int,
    channels: ChannelsPlugin,
    viewer_store: ThreadViewerStore,
):
    viewer_ids = await viewer_store.add_viewer(thread_id, user_id)
    join_message = UserJoinedMessage(
        user_id=sqid_encode(user_id),
        viewers=[sqid_encode(viewer) for viewer in viewer_ids],
    )
    channels.publish(
        encode_server_message_str(join_message), [get_thread_channel(thread_id)]
    )

    logger.info(f"WebSocket connected: user {user_id} -> thread {thread_id}")


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
    viewer_store: ThreadViewerStore,
    team_id: int,
) -> AsyncGenerator[None, None]:
    thread = await get_or_create_thread(
        transaction=transaction,
        threadable_type=threadable_type,
        threadable_id=threadable_id,
        team_id=team_id,
    )

    user_id = socket.user
    await handle_user_joined(thread.id, user_id, channels, viewer_store)

    async with channels.start_subscription(
        [get_thread_channel(thread.id)]
    ) as subscriber:
        try:
            # Background task sends all incoming messages to WebSocket
            async with subscriber.run_in_background(socket.send_text):
                # Store connection state for handler
                socket.state["thread_id"] = thread.id
                socket.state["user_id"] = user_id
                yield
        except WebSocketDisconnect:
            pass
        finally:
            # Remove viewer from MemoryStore and get updated list
            viewer_ids = await viewer_store.remove_viewer(thread.id, user_id)

            # Notify other users that someone left
            left_message = UserLeftMessage(
                user_id=sqid_encode(user_id),
                viewers=[sqid_encode(viewer) for viewer in viewer_ids],
            )
            channels.publish(
                encode_server_message_str(left_message), [get_thread_channel(thread.id)]
            )

            logger.info(
                f"WebSocket disconnected: user {user_id} from thread {thread.id}"
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
    viewer_store: ThreadViewerStore,
) -> ServerMessage | None:
    """Handle incoming client messages (typing indicators and mark-read requests)."""
    # Get connection state
    thread_id: int = socket.state["thread_id"]
    user_id: int = socket.state["user_id"]

    # Route to appropriate handler based on message type
    match data:
        case TypingMessage():
            await handle_typing_message(
                data, thread_id, user_id, channels, viewer_store
            )
        case MarkReadMessage():
            await handle_mark_read_message(thread_id, user_id, transaction)
