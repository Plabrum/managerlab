"""WebSocket handler for real-time thread updates using PostgreSQL LISTEN/NOTIFY."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from litestar import WebSocket
from litestar.handlers import WebsocketListener
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guards import requires_user_scope
from app.threads.models import Thread
from app.threads.services import notify_thread

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


class ThreadWebSocketHandler(WebsocketListener):
    path = "/ws/threads/{threadable_type:str}/{threadable_id:int}"
    guards = [requires_user_scope]

    async def on_accept(
        self,
        socket: WebSocket,
        threadable_type: str,
        threadable_id: int,
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
        self.user_id = socket.user.id
        self.user_name = socket.user.name

        # Get engine for LISTEN connection (needs separate connection from pool)
        engine = transaction.get_bind()

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
            f"WebSocket connected: user {socket.user} -> thread {self.thread_id}"
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

    async def on_receive(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle client messages: ping/pong and typing indicators."""
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
                            "user_id": self.user_id,
                            "is_typing": is_typing,
                            "viewers": self._get_viewers_list(),
                        }

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
                # psycopg3 async iterator - yields notifications as they arrive
                async for notify in raw_conn.notifies():
                    message = json.loads(notify.payload)
                    await socket.send_json(message)
                    logger.debug(f"Forwarded notification: {message.get('type')}")
