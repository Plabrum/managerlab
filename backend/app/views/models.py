from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.objects.enums import ObjectTypes
from app.utils.sqids import Sqid

if TYPE_CHECKING:
    from app.teams.models import Team
    from app.users.models import User


class SavedView(RLSMixin(), BaseDBModel):
    """Saved view configuration for list pages.

    SavedView instances store complete list page state including display mode, filters,
    column visibility, sorting, and search settings. They can be either personal
    (owned by a user) or team-shared (accessible to all team members).

    All saved views are scoped to a team via RLS. The user_id field determines
    ownership:
    - Personal views: user_id is set, only that user can edit/delete
    - Team-shared views: user_id is NULL, any team member can view (not edit/delete)

    Default views:
    - Only personal views can be marked as default (is_default=True)
    - Each user can have ONE default view per object_type
    - Database partial unique index enforces uniqueness
    - When default view is deleted, user falls back to hard-coded default
    """

    __tablename__ = "saved_views"

    # Identification
    name: Mapped[str] = mapped_column(sa.Text, nullable=False, index=True)
    object_type: Mapped[ObjectTypes] = mapped_column(
        sa.Text,
        nullable=False,
        index=True,
    )

    # Configuration storage (TanStack Table state + display mode)
    config: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    # Schema version for future migrations
    schema_version: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        server_default=sa.text("1"),
    )

    # Default flag (only personal views can be default)
    is_default: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("false"),
        index=True,
    )

    # Ownership (NULL = team-shared, set = personal)
    user_id: Mapped[Sqid | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    team: Mapped["Team"] = relationship("Team", foreign_keys="[SavedView.team_id]")

    # Table constraints
    __table_args__ = (
        # Unique view name per owner (user or team) and object type
        sa.UniqueConstraint(
            "team_id",
            "user_id",
            "object_type",
            "name",
            name="unique_view_name_per_owner_and_object",
        ),
        # Index for efficient lookups by team and object type
        sa.Index("ix_saved_views_team_object", "team_id", "object_type"),
        # Ensure only one default per user per object_type (personal views only)
        sa.Index(
            "ix_saved_views_one_default_per_user_object",
            "user_id",
            "object_type",
            unique=True,
            postgresql_where=sa.text("is_default = true AND user_id IS NOT NULL"),
        ),
    )

    @property
    def is_personal(self) -> bool:
        """Check if this is a personal view (owned by a user)."""
        return self.user_id is not None

    @property
    def is_team_shared(self) -> bool:
        """Check if this is a team-shared view (accessible to all team members)."""
        return self.user_id is None
