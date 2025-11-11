"""Magic link authentication business logic."""

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import MagicLinkToken
from app.auth.tokens import build_magic_link_url, generate_secure_token, hash_token
from app.emails.service import EmailService
from app.users.models import User

__all__ = ["MagicLinkService"]


class MagicLinkService:
    """Service for handling magic link authentication."""

    def __init__(self, db_session: AsyncSession, email_service: EmailService):
        """Initialize the magic link service.

        Args:
            db_session: Database session
            email_service: Email service for sending magic links
        """
        self.db = db_session
        self.email_service = email_service

    async def create_and_send_magic_link(self, email: str) -> dict[str, Any]:
        """Create a magic link token and send it via email.

        Args:
            email: Email address to send magic link to

        Returns:
            Dictionary with status information

        Note:
            This creates a new user if they don't exist (passwordless registration).
        """
        email = email.lower().strip()

        # Check if user exists
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # Create new user (passwordless registration)
            user = User(
                email=email,
                name=email.split("@")[0],  # Use email prefix as default name
                email_verified=False,
            )
            self.db.add(user)
            await self.db.flush()  # Flush to get user.id

        # Generate token
        token = generate_secure_token()
        token_hash = hash_token(token)

        # Create token record
        magic_link_token = MagicLinkToken.create_for_user(
            user_id=user.id,
            token_hash=token_hash,
            expires_in_minutes=15,
        )
        self.db.add(magic_link_token)
        await self.db.flush()  # Flush to ensure token is created

        # Build the magic link URL
        magic_link_url = build_magic_link_url(token)

        # Send email
        await self.email_service.send_magic_link_email(
            to_email=email,
            magic_link_url=magic_link_url,
            expires_minutes=15,
        )

        return {"success": True, "message": "A magic link has been sent to your email."}

    async def verify_magic_link_token(self, token: str) -> User | None:
        """Verify a magic link token and return the associated user.

        Args:
            token: The plaintext token from the URL

        Returns:
            User object if token is valid, None otherwise

        Note:
            This automatically marks the token as used if valid.
        """
        token_hash = hash_token(token)

        # Find the token with pessimistic lock to prevent race conditions
        result = await self.db.execute(
            select(MagicLinkToken)
            .where(MagicLinkToken.token_hash == token_hash)
            .where(MagicLinkToken.used_at.is_(None))
            .with_for_update()  # Prevent concurrent use of same token
        )
        magic_link_token = result.scalar_one_or_none()

        if not magic_link_token:
            return None

        # Check if expired
        if not magic_link_token.is_valid():
            return None

        # Mark as used
        magic_link_token.mark_as_used()

        # Get the user
        result = await self.db.execute(select(User).where(User.id == magic_link_token.user_id))
        user = result.scalar_one_or_none()

        return user
