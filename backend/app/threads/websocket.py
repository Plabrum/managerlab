import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from litestar import WebSocket
from litestar.channels import ChannelsPlugin
from litestar.exceptions import WebSocketDisconnect
from litestar.handlers import websocket_listener
import msgspec
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guards import requires_user_scope
from app.objects.enums import ObjectTypes
from app.threads.enums import ThreadSocketMessageType
from app.threads.services import (
    ThreadViewerStore,
    get_or_create_thread,
    mark_thread_as_read,
    notify_thread,
)
from app.threads.schemas import ClientMessage, ServerMessage
from app.threads.utils import get_thread_channel
from app.utils.sqids import Sqid, sqid_encode

logger = logging.getLogger(__name__)


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
    viewer_ids = await viewer_store.add_viewer(thread.id, user_id)

    await notify_thread(
        channels,
        thread.id,
        ServerMessage(
            message_type=ThreadSocketMessageType.USER_JOINED,
            user_id=sqid_encode(user_id),
            viewers=[sqid_encode(viewer) for viewer in viewer_ids],
        ),
    )

    logger.info(f"WebSocket connected: user {user_id} -> thread {thread.id}")

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
            left_message = ServerMessage(
                message_type=ThreadSocketMessageType.USER_LEFT,
                user_id=sqid_encode(user_id),
                viewers=[sqid_encode(viewer) for viewer in viewer_ids],
            )

            await notify_thread(channels, thread.id, left_message)

            logger.info(
                f"WebSocket disconnected: user {user_id} from thread {thread.id}"
            )


@websocket_listener(
    "/ws/threads/{threadable_type:str}/{threadable_id:str}",
    connection_lifespan=thread_connection_lifespan,
    guards=[requires_user_scope],
)
async def thread_handler(
    data: dict,
    channels: ChannelsPlugin,
    socket: WebSocket,
    transaction: AsyncSession,
    viewer_store: ThreadViewerStore,
) -> None:
    thread_id: int = socket.state["thread_id"]
    user_id: int = socket.state["user_id"]
    # Convert dict to ClientMessage using msgspec
    message: ClientMessage = msgspec.convert(data, ClientMessage)
    # Route to appropriate handler based on message type
    match message.message_type:
        case ThreadSocketMessageType.USER_FOCUS | ThreadSocketMessageType.USER_BLUR:
            viewer_ids = await viewer_store.add_viewer(thread_id, user_id)
            await notify_thread(
                channels,
                thread_id,
                ServerMessage(
                    message_type=message.message_type,
                    user_id=sqid_encode(user_id),
                    viewers=[sqid_encode(viewer) for viewer in viewer_ids],
                ),
            )
        case ThreadSocketMessageType.MARK_READ:
            await mark_thread_as_read(transaction, thread_id, user_id)
            await transaction.commit()
