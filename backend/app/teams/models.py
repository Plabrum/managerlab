from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel

if TYPE_CHECKING:
    from app.auth.models import TeamInvitationToken
    from app.users.models import Role


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

    # Relationship to invitation tokens
    invitation_tokens: Mapped[list["TeamInvitationToken"]] = relationship(
        "app.auth.models.TeamInvitationToken",
        back_populates="team",
        cascade="all, delete-orphan",
    )
