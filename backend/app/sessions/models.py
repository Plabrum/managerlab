"""Session models for PostgreSQL-backed session storage."""

from datetime import datetime, timezone
from typing import Dict, Any
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.base.models import BaseDBModel


class Session(BaseDBModel.registry.generate_base()):
    """Session storage model for PostgreSQL-backed sessions.

    Note: Inherits directly from DeclarativeBase instead of BaseDBModel
    to avoid soft delete functionality and extra columns. Sessions use
    expiration-based cleanup via expires_at.
    """

    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(
        sa.String(255), primary_key=True, index=True
    )
    data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    expires_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<Session(session_id={self.session_id}, expires_at={self.expires_at})>"

    @property
    def is_expired(self) -> bool:
        """Check if the session is expired."""
        return datetime.now(tz=timezone.utc) > self.expires_at
