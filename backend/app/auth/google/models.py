from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.users.models import User
from app.utils.sqids import Sqid


class GoogleOAuthAccount(BaseDBModel):
    """Model for storing Google OAuth account information."""

    __tablename__ = "google_oauth_accounts"

    user_id: Mapped[Sqid] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    google_id: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    picture: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    access_token: Mapped[str] = mapped_column(sa.Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    # Relationship back to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="google_accounts",
        innerjoin=True,
    )


class GoogleOAuthState(BaseDBModel):
    """Model for storing OAuth state tokens to prevent CSRF attacks.

    The return_url field stores where to redirect the user after successful OAuth,
    enabling preview deployments to work correctly by preserving the original frontend URL.
    """

    __tablename__ = "google_oauth_states"

    state: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True, nullable=False)
    return_url: Mapped[str] = mapped_column(sa.Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
