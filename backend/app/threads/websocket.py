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

logger = logging.getLogger(__name__)


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

        # Get engine for LISTEN connection (needs separate connection from pool)
        engine = transaction.get_bind()

        # Start PostgreSQL LISTEN in background
        self.listen_task = asyncio.create_task(
            self._listen_for_notifications(socket, self.thread_id, engine)
        )

        logger.info(
            f"WebSocket connected: user {socket.user} -> thread {self.thread_id}"
        )

    async def on_disconnect(self, socket: WebSocket) -> None:
        """Cancel the LISTEN task."""
        if hasattr(self, "listen_task"):
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass

        logger.info(
            f"WebSocket disconnected from thread {getattr(self, 'thread_id', None)}"
        )

    async def on_receive(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle ping/pong for keepalive."""
        if data.get("type") == "ping":
            return {"type": "pong", "timestamp": data.get("timestamp")}
        return {"type": "error", "message": "Unknown message type"}

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
