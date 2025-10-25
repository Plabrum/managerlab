"""Event models for tracking object lifecycle changes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.events.enums import EventType

if TYPE_CHECKING:
    from app.users.models import User


class Event(RLSMixin(), BaseDBModel):
    """
    Append-only event log for object lifecycle tracking.

    Records structured events (create, update, delete) with associated data.
    Events are processed by registered consumers for downstream actions.

    Team-scoped via RLS for data isolation.
    """

    __tablename__ = "events"

    # Actor - who triggered the event
    actor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    actor: Mapped[User] = relationship("User", foreign_keys=[actor_id], lazy="joined")

    # Object - what was acted upon (polymorphic)
    object_type: Mapped[str] = mapped_column(String(50), nullable=False)
    object_id: Mapped[int] = mapped_column(nullable=False)

    # Event type
    event_type: Mapped[EventType] = mapped_column(nullable=False)

    # Structured event data (changes, metadata, etc.)
    # Format examples:
    # - CREATED: {"name": "Campaign Name", "status": "draft"}
    # - UPDATED: {"name": {"old": "Old Name", "new": "New Name"}}
    # - DELETED: {"name": "Campaign Name"}
    # - STATE_CHANGED: {"state": {"old": "draft", "new": "active"}}
    event_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        # Index for fetching object-specific event timeline
        Index(
            "ix_events_team_object",
            "team_id",
            "object_type",
            "object_id",
            "created_at",
        ),
        # Index for team-wide event feed
        Index("ix_events_team_created", "team_id", "created_at"),
        # Index for actor-specific events
        Index("ix_events_actor", "actor_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Event({self.event_type.value}: {self.object_type}#{self.object_id} by User#{self.actor_id})>"
