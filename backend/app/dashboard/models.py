"""Dashboard models for storing user and team dashboard configurations."""

from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin

if TYPE_CHECKING:
    from app.teams.models import Team
    from app.users.models import User


class Dashboard(RLSMixin(), BaseDBModel):
    """Dashboard configuration storage for users and teams.

    All dashboards belong to a team (via RLSMixin's team_id).
    - Personal dashboards: user_id is set, visible only to that user within the team
    - Team dashboards: user_id is NULL, visible to all team members
    """

    __tablename__ = "dashboards"

    # Dashboard identification
    name: Mapped[str] = mapped_column(sa.Text, nullable=False, index=True)

    # JSON configuration storage (graphs, queries, headers, layout)
    config: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    # Personal dashboard owner (NULL = team-wide dashboard)
    user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Default dashboard flag
    is_default: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("false"),
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    team: Mapped["Team"] = relationship("Team", foreign_keys="Dashboard.team_id")

    # Table constraints
    __table_args__ = (
        # Unique dashboard names per user within a team
        sa.UniqueConstraint(
            "team_id",
            "user_id",
            "name",
            name="unique_dashboard_name_per_owner",
        ),
    )

    @property
    def is_personal(self) -> bool:
        """Check if this is a personal dashboard."""
        return self.user_id is not None

    @property
    def is_team_wide(self) -> bool:
        """Check if this is a team-wide dashboard."""
        return self.user_id is None
