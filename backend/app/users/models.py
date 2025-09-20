from sqlalchemy.orm import mapped_column, relationship, Mapped
import sqlalchemy as sa
from typing import List, TYPE_CHECKING

from app.base.models import BaseDBModel


if TYPE_CHECKING:
    from auth.google.models import GoogleOAuthAccount


class User(BaseDBModel):
    __tablename__ = "users"
    name = mapped_column(sa.Text, index=True, nullable=False)
    email = mapped_column(sa.Text, unique=True, index=True, nullable=False)
    email_verified = mapped_column(sa.Boolean, default=False, nullable=False)

    # Relationship to Google OAuth accounts
    google_accounts: Mapped[List["GoogleOAuthAccount"]] = relationship(
        "GoogleOAuthAccount", back_populates="user", cascade="all, delete-orphan"
    )


class WaitlistEntry(BaseDBModel):
    __tablename__ = "waitlist_entries"
    name = mapped_column(sa.Text, index=True, nullable=False)
    email = mapped_column(sa.Text, index=True, nullable=False)
    company = mapped_column(sa.Text, nullable=True)
    message = mapped_column(sa.Text, nullable=True)
