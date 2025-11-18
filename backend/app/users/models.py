from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic_utils.pg_policy import PGPolicy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLS_POLICY_REGISTRY, RLSMixin
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
    __table_args__ = (sa.UniqueConstraint("user_id", "team_id", name="uq_user_team"),)


# Register custom RLS policy for users table (role-based access)
# Use NULLIF to convert empty strings to NULL, and check is_system_mode first
_users_rls_policy = PGPolicy(
    schema="public",
    signature="team_member_access_policy",
    on_entity="public.users",
    definition="""AS PERMISSIVE
                        FOR ALL
                        USING (
                            NULLIF(current_setting('app.is_system_mode', true), '')::boolean IS TRUE
                            OR (NULLIF(current_setting('app.team_id', true), '') IS NOT NULL
                                AND id IN (
                                    SELECT user_id FROM roles
                                    WHERE team_id = NULLIF(current_setting('app.team_id', true), '')::int
                                ))
                        )""",
)
RLS_POLICY_REGISTRY.append(_users_rls_policy)

# Register RLS enablement for users table
if "rls" not in BaseDBModel.metadata.info:
    BaseDBModel.metadata.info["rls"] = set()
BaseDBModel.metadata.info["rls"].add("users")
