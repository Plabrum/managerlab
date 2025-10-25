"""WebSocket handler for real-time thread updates using PostgreSQL LISTEN/NOTIFY."""

import asyncio
from app.users.models import User
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from litestar import WebSocket
from litestar.handlers import WebsocketListener
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guards import requires_user_scope
from app.objects.enums import ObjectTypes
from app.threads.models import Thread
from app.threads.services import notify_thread, mark_thread_as_read
from app.utils.sqids import Sqid, sqid_encode

logger = logging.getLogger(__name__)

# In-memory tracking for active viewers per thread
# Structure: {thread_id: {user_id: {"name": str, "is_typing": bool}}}
active_viewers: dict[int, dict[int, dict[str, Any]]] = {}


@asynccontextmanager
async def postgres_listen(raw_conn: Any, channel: str):
    await raw_conn.execute(f"LISTEN {channel};")
    logger.debug(f"Started LISTEN on channel: {channel}")
    try:
        yield
    finally:
        await raw_conn.execute(f"UNLISTEN {channel};")
        logger.debug(f"Stopped LISTEN on channel: {channel}")


@asynccontextmanager
async def safe_websocket_sender(socket: WebSocket):
    """Context manager that safely handles WebSocket send operations."""

    class WebSocketSender:
        def __init__(self, ws: WebSocket):
            self.ws = ws
            self.is_closed = False

        async def send_json(self, data: dict[str, Any]) -> bool:
            """Send JSON data. Returns False if connection is closed."""
            if self.is_closed:
                return False
            try:
                await self.ws.send_json(data)
                return True
            except RuntimeError as e:
                if "after sending 'websocket.close'" in str(e):
                    self.is_closed = True
                    logger.debug("WebSocket already closed")
                    return False
                raise

    sender = WebSocketSender(socket)
    try:
        yield sender
    finally:
        sender.is_closed = True


class ThreadWebSocketHandler(WebsocketListener):
    path = "/ws/threads/{threadable_type:str}/{threadable_id:str}"
    guards = [requires_user_scope]

    async def on_accept(
        self,
        socket: WebSocket,
        threadable_type: ObjectTypes,
        threadable_id: Sqid,
        transaction: AsyncSession,
    ) -> None:
        """Verify thread access and start listening for notifications."""
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

        self.thread_id = thread.id
        # socket.user is already the user_id (int), not a User object
        self.user_id = socket.user

        # Load user name from database
        user_stmt = select(User).where(User.id == self.user_id)
        user_result = await transaction.execute(user_stmt)
        user = user_result.scalar_one()
        self.user_name = user.name

        # Get engine for LISTEN connection (needs separate connection from pool)
        engine = transaction.get_bind()
        self.engine = engine  # Store for later use in on_receive

        # Track this user as viewing the thread
        if self.thread_id not in active_viewers:
            active_viewers[self.thread_id] = {}

        active_viewers[self.thread_id][self.user_id] = {
            "name": self.user_name,
            "is_typing": False,
        }

        # Notify other users that someone joined
        await notify_thread(
            transaction,
            self.thread_id,
            {
                "type": "user_joined",
                "user_id": self.user_id,
                "viewers": self._get_viewers_list(),
            },
        )

        # Start PostgreSQL LISTEN in background
        self.listen_task = asyncio.create_task(
            self._listen_for_notifications(socket, self.thread_id, engine)
        )

        logger.info(
            f"WebSocket connected: user {self.user_id} ({self.user_name}) -> thread {self.thread_id}"
        )

    async def on_disconnect(self, socket: WebSocket) -> None:
        """Cancel the LISTEN task and remove user from viewers."""
        if hasattr(self, "listen_task"):
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass

        # Remove user from active viewers
        if hasattr(self, "thread_id") and hasattr(self, "user_id"):
            if self.thread_id in active_viewers:
                active_viewers[self.thread_id].pop(self.user_id, None)

                # Clean up empty thread entries
                if not active_viewers[self.thread_id]:
                    del active_viewers[self.thread_id]

                # Notify remaining users that someone left
                # We need a session here, but we're disconnecting so we'll skip the notification
                # Frontend will handle stale presence via timeout

        logger.info(
            f"WebSocket disconnected from thread {getattr(self, 'thread_id', None)}"
        )

    async def on_receive(
        self, data: dict[str, Any], transaction: AsyncSession
    ) -> dict[str, Any]:
        """Handle client messages: ping/pong, typing indicators, and mark-read."""
        msg_type = data.get("type")

        if msg_type == "ping":
            return {"type": "pong", "timestamp": data.get("timestamp")}

        elif msg_type == "typing":
            # Update typing status
            is_typing = data.get("is_typing", False)

            if hasattr(self, "thread_id") and hasattr(self, "user_id"):
                if self.thread_id in active_viewers:
                    if self.user_id in active_viewers[self.thread_id]:
                        active_viewers[self.thread_id][self.user_id]["is_typing"] = (
                            is_typing
                        )

                        # Broadcast typing status to other users (don't return to sender)
                        # We'll use the notification system for this
                        return {
                            "type": "typing_update",
                            "user_id": sqid_encode(self.user_id),
                            "is_typing": is_typing,
                            "viewers": self._get_viewers_list(),
                        }

        elif msg_type == "mark_read":
            # Mark thread as read for this user
            if (
                hasattr(self, "thread_id")
                and hasattr(self, "user_id")
                and hasattr(self, "engine")
            ):
                # Create a new async session from the engine
                await mark_thread_as_read(transaction, self.thread_id, self.user_id)
                await transaction.commit()
                return {"type": "marked_read"}

        return {"type": "error", "message": "Unknown message type"}

    def _get_viewers_list(self) -> list[dict[str, Any]]:
        """Get list of current viewers with their typing status."""
        if not hasattr(self, "thread_id") or self.thread_id not in active_viewers:
            return []

        return [
            {
                "user_id": user_id,
                "name": info["name"],
                "is_typing": info["is_typing"],
            }
            for user_id, info in active_viewers[self.thread_id].items()
        ]

    async def _listen_for_notifications(
        self,
        socket: WebSocket,
        thread_id: int,
        engine: Any,
    ) -> None:
        """Listen for PostgreSQL notifications and forward to WebSocket."""
        channel = f"thread_{thread_id}"

        # Create a new connection for LISTEN (separate from transaction pool)
        async with engine.connect() as conn:
            raw_conn = await conn.get_raw_connection()

            # Context manager handles LISTEN/UNLISTEN automatically
            async with postgres_listen(raw_conn, channel):
                async with safe_websocket_sender(socket) as sender:
                    # psycopg3 async iterator - yields notifications as they arrive
                    async for notify in raw_conn.notifies():
                        message = json.loads(notify.payload)
                        if not await sender.send_json(message):
                            # Connection closed, stop listening
                            break
                        logger.debug(f"Forwarded notification: {message.get('type')}")
