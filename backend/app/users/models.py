from sqlalchemy.orm import mapped_column, relationship, Mapped
import sqlalchemy as sa
from typing import TYPE_CHECKING
from app.base.models import BaseDBModel
from app.state_machine.models import StateMachineMixin
from app.users.enums import UserStates, RoleLevel


if TYPE_CHECKING:
    from app.auth.google.models import GoogleOAuthAccount


class User(
    StateMachineMixin(state_enum=UserStates, initial_state=UserStates.NEEDS_TEAM),
    BaseDBModel,
):
    """Platform user account - represents people who log into the system."""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(sa.Text, index=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.Text, unique=True, index=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False
    )

    # Relationship to Google OAuth accounts
    google_accounts: Mapped[list["GoogleOAuthAccount"]] = relationship(
        back_populates="user",
        innerjoin=True,
    )

    # Relationship to roles (team memberships)
    roles: Mapped[list["Role"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Team(BaseDBModel):
    """Organization/workspace that users belong to."""

    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(sa.Text, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Relationship to roles (team members)
    roles: Mapped[list["Role"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
    )


class Role(BaseDBModel):
    """Join table linking Users to Teams with a role level."""

    __tablename__ = "roles"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    team_id: Mapped[int] = mapped_column(
        sa.ForeignKey("teams.id", ondelete="CASCADE"),
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
    __table_args__ = (sa.UniqueConstraint("user_id", "team_id", name="uq_user_team"),)


class WaitlistEntry(BaseDBModel):
    __tablename__ = "waitlist_entries"
    name = mapped_column(sa.Text, index=True, nullable=False)
    email = mapped_column(sa.Text, index=True, nullable=False)
    company = mapped_column(sa.Text, nullable=True)
    message = mapped_column(sa.Text, nullable=True)
