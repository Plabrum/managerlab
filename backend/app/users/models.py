from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.state_machine.models import StateMachineMixin
from app.users.enums import RoleLevel, UserStates

if TYPE_CHECKING:
    from app.auth.google.models import GoogleOAuthAccount
    from app.auth.models import MagicLinkToken
    from app.teams.models import Team


class User(
    StateMachineMixin(state_enum=UserStates, initial_state=UserStates.NEEDS_TEAM),
    BaseDBModel,
):
    """Platform user account - represents people who log into the system."""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(sa.Text, index=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.Text, unique=True, index=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    # Relationship to Google OAuth accounts
    google_accounts: Mapped[list["GoogleOAuthAccount"]] = relationship(
        "app.auth.google.models.GoogleOAuthAccount",
        back_populates="user",
        innerjoin=True,
    )

    # Relationship to roles (team memberships)
    roles: Mapped[list["Role"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Relationship to magic link tokens
    magic_link_tokens: Mapped[list["MagicLinkToken"]] = relationship(
        "app.auth.models.MagicLinkToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Computed relationship: the team where this user is OWNER
    # Users can only be OWNER of one team (enforced by partial unique index)
    primary_team: Mapped["Team | None"] = relationship(
        "Team",
        secondary="roles",
        primaryjoin="User.id == Role.user_id",
        secondaryjoin="and_(Role.team_id == Team.id, Role.role_level == 'OWNER')",
        viewonly=True,
        uselist=False,
    )

    @hybrid_property
    def primary_team_id(self) -> int | None:
        """Returns the ID of the team where this user is OWNER, or None."""
        return self.primary_team.id if self.primary_team else None


class Role(BaseDBModel):
    """Join table linking Users to Teams with a role level.

    Note: This table does NOT have RLS because it defines team membership.
    Users must be able to see all their roles across all teams to switch teams.
    """

    __tablename__ = "roles"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    team_id: Mapped[int] = mapped_column(
        sa.ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role_level: Mapped[RoleLevel] = mapped_column(
        sa.Enum(RoleLevel, native_enum=False, length=50),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="roles")
    team: Mapped["Team"] = relationship(back_populates="roles")

    # Unique constraint: a user can only have one role per team
    # Partial unique index: a user can only be OWNER of one team
    __table_args__ = (
        sa.UniqueConstraint("user_id", "team_id", name="uq_user_team"),
        sa.Index(
            "ix_user_single_owner",
            "user_id",
            unique=True,
            postgresql_where=sa.text("role_level = 'OWNER'"),
        ),
    )
