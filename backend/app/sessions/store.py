"""PostgreSQL-backed session store implementation."""

import json
from datetime import UTC, datetime, timedelta
from typing import Any

from litestar.stores.base import Store
from sqlalchemy import delete, select

from app.sessions.models import Session


class PostgreSQLSessionStore(Store):
    """PostgreSQL-backed session store for Litestar."""

    def __init__(self, db_session_factory, default_expiry: int = 3600):
        """Initialize the PostgreSQL session store.

        Args:
            db_session_factory: Factory function to create database sessions
            default_expiry: Default session expiry time in seconds
        """
        self.db_session_factory = db_session_factory
        self.default_expiry = default_expiry

    async def get(self, key: str, renew_for: int | timedelta | None = None) -> Any:
        """Get session data by key."""
        async with self.db_session_factory() as db_session:
            stmt = select(Session).where(Session.session_id == key)
            result = await db_session.execute(stmt)
            session = result.scalar_one_or_none()

            if not session:
                return None

            # Check if session is expired
            if session.is_expired:
                # Clean up expired session
                await db_session.delete(session)
                await db_session.commit()
                return None

            # Renew session if requested
            if renew_for is not None:
                if isinstance(renew_for, timedelta):
                    session.expires_at = datetime.now(tz=UTC) + renew_for
                else:
                    session.expires_at = datetime.now(tz=UTC) + timedelta(seconds=renew_for)
                await db_session.commit()

            # Convert dict back to bytes for Litestar
            return json.dumps(session.data).encode("utf-8")

    async def set(self, key: str, value: str | bytes, expires_in: int | timedelta | None = None) -> None:
        """Set session data by key."""
        if expires_in is None:
            expiry_seconds = self.default_expiry
        elif isinstance(expires_in, timedelta):
            expiry_seconds = int(expires_in.total_seconds())
        else:
            expiry_seconds = expires_in

        expires_at = datetime.now(tz=UTC) + timedelta(seconds=expiry_seconds)

        # Convert value to string for JSON parsing
        if isinstance(value, bytes):
            value_str = value.decode("utf-8")
        else:
            value_str = value

        # Convert to dict for storage in JSONB
        try:
            session_data = json.loads(value_str)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # If data can't be decoded as JSON, store it as a string value
            session_data = {"raw_data": value_str}

        async with self.db_session_factory() as db_session:
            # Try to get existing session
            stmt = select(Session).where(Session.session_id == key)
            result = await db_session.execute(stmt)
            session = result.scalar_one_or_none()

            if session:
                # Update existing session
                session.data = session_data
                session.expires_at = expires_at
            else:
                # Create new session
                session = Session(session_id=key, data=session_data, expires_at=expires_at)
                db_session.add(session)

            await db_session.commit()

    async def delete(self, key: str) -> None:
        """Delete session by key."""
        async with self.db_session_factory() as db_session:
            stmt = delete(Session).where(Session.session_id == key)
            await db_session.execute(stmt)
            await db_session.commit()

    async def exists(self, key: str) -> bool:
        """Check if session exists and is not expired."""
        async with self.db_session_factory() as db_session:
            stmt = select(Session).where(Session.session_id == key)
            result = await db_session.execute(stmt)
            session = result.scalar_one_or_none()

            if not session:
                return False

            if session.is_expired:
                # Clean up expired session
                await db_session.delete(session)
                await db_session.commit()
                return False

            return True

    async def expires_in(self, key: str) -> int | None:
        """Get seconds until session expires."""
        async with self.db_session_factory() as db_session:
            stmt = select(Session).where(Session.session_id == key)
            result = await db_session.execute(stmt)
            session = result.scalar_one_or_none()

            if not session or session.is_expired:
                return None

            now = datetime.now(tz=UTC)
            delta = session.expires_at - now
            return max(0, int(delta.total_seconds()))

    async def delete_expired(self) -> None:
        """Clean up expired sessions."""
        async with self.db_session_factory() as db_session:
            now = datetime.now(tz=UTC)
            stmt = delete(Session).where(Session.expires_at < now)
            await db_session.execute(stmt)
            await db_session.commit()

    async def delete_all(self) -> None:
        """Delete all sessions."""
        async with self.db_session_factory() as db_session:
            stmt = delete(Session)
            await db_session.execute(stmt)
            await db_session.commit()
