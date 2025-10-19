"""Dashboard models for storing user and team dashboard configurations."""

from typing import Any, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

from app.base.models import BaseDBModel
from app.dashboard.enums import DashboardOwnerType

if TYPE_CHECKING:
    from app.users.models import User, Team


class Dashboard(BaseDBModel):
    """Dashboard configuration storage for users and teams."""

    __tablename__ = "dashboards"

    # Dashboard identification
    name: Mapped[str] = mapped_column(sa.Text, nullable=False, index=True)

    # JSON configuration storage (graphs, queries, headers, layout)
    config: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    # Ownership type
    owner_type: Mapped[DashboardOwnerType] = mapped_column(
        sa.Enum(
            DashboardOwnerType,
            native_enum=False,
            length=10,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )

    # Foreign keys for ownership (one must be set based on owner_type)
    user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    team_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("teams.id", ondelete="CASCADE"),
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
    team: Mapped["Team | None"] = relationship("Team", foreign_keys=[team_id])

    # Table constraints
    __table_args__ = (
        # Ensure owner_type matches the set foreign key
        sa.CheckConstraint(
            "(owner_type = 'user' AND user_id IS NOT NULL AND team_id IS NULL) OR "
            "(owner_type = 'team' AND team_id IS NOT NULL AND user_id IS NULL)",
            name="check_owner_type_matches",
        ),
        # Unique dashboard names per user
        sa.UniqueConstraint(
            "user_id",
            "name",
            name="unique_user_dashboard_name",
        ),
        # Unique dashboard names per team
        sa.UniqueConstraint(
            "team_id",
            "name",
            name="unique_team_dashboard_name",
        ),
    )
