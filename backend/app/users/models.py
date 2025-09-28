from sqlalchemy.orm import mapped_column, relationship, Mapped
import sqlalchemy as sa
from typing import TYPE_CHECKING
from app.base.models import BaseDBModel
from app.state_machine.models import StateMachineMixin
from app.users.enums import UserStates


if TYPE_CHECKING:
    from auth.google.models import GoogleOAuthAccount


class User(
    StateMachineMixin(states=UserStates, initial_state=UserStates.NEEDS_TEAM),
    BaseDBModel,
):
    __tablename__ = "users"
    name = mapped_column(sa.Text, index=True, nullable=False)
    email = mapped_column(sa.Text, unique=True, index=True, nullable=False)
    email_verified = mapped_column(sa.Boolean, default=False, nullable=False)

    # Relationship to Google OAuth accounts
    google_accounts: Mapped[list["GoogleOAuthAccount"]] = relationship(
        back_populates="user",
        innerjoin=True,
    )


class WaitlistEntry(BaseDBModel):
    __tablename__ = "waitlist_entries"
    name = mapped_column(sa.Text, index=True, nullable=False)
    email = mapped_column(sa.Text, index=True, nullable=False)
    company = mapped_column(sa.Text, nullable=True)
    message = mapped_column(sa.Text, nullable=True)


class Team(BaseDBModel):
    __tablename__ = "teams"

    # Team-specific fields
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
