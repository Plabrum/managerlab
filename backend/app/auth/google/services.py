import secrets
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.config import Config
from app.users.models import User
from app.auth.google.models import GoogleOAuthAccount, GoogleOAuthState


class GoogleOAuthService:
    """Service for handling Google OAuth authentication."""

    def __init__(
        self,
        config: Config,
        transaction: AsyncSession,
        http_client: aiohttp.ClientSession,
    ):
        self.config = config
        self.http_client = http_client
        self.transaction = transaction
        self.client_id = config.GOOGLE_CLIENT_ID
        self.client_secret = config.GOOGLE_CLIENT_SECRET
        self.redirect_uri = config.GOOGLE_REDIRECT_URI
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    def generate_auth_url(self, redirect_uri: Optional[str] = None) -> tuple[str, str]:
        """Generate Google OAuth authorization URL and state token."""
        state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri or self.redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }

        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(params)}"
        return auth_url, state

    async def store_oauth_state(
        self, transaction: AsyncSession, state: str, redirect_uri: Optional[str] = None
    ) -> GoogleOAuthState:
        """Store OAuth state in database for CSRF protection."""
        oauth_state = GoogleOAuthState(
            state=state,
            redirect_uri=redirect_uri,
            expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=10),
        )
        transaction.add(oauth_state)
        return oauth_state

    async def verify_oauth_state(
        self, transaction: AsyncSession, state: str
    ) -> Optional[GoogleOAuthState]:
        """Verify OAuth state token and return stored state if valid."""
        stmt = select(GoogleOAuthState).where(
            GoogleOAuthState.state == state,
            GoogleOAuthState.expires_at > datetime.now(tz=timezone.utc),
        )
        result = await transaction.execute(stmt)
        oauth_state = result.scalar_one_or_none()

        if oauth_state:
            await transaction.delete(oauth_state)

        return oauth_state

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        async with self.http_client.post(self.token_url, data=data) as response:
            response.raise_for_status()
            return await response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google using access token."""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with self.http_client.get(self.userinfo_url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def create_or_update_user(
        self,
        transaction: AsyncSession,
        google_user_info: Dict[str, Any],
        tokens: Dict[str, Any],
    ) -> User:
        """Create or update user from Google OAuth information."""
        google_id = google_user_info["id"]
        email = google_user_info["email"]
        name = google_user_info["name"]
        picture = google_user_info.get("picture")

        # Check if Google account already exists
        stmt = (
            select(GoogleOAuthAccount)
            .where(GoogleOAuthAccount.google_id == google_id)
            .options(joinedload(GoogleOAuthAccount.user))
        )
        result = await transaction.execute(stmt)
        google_account = result.scalar_one_or_none()

        if google_account:
            # Update existing account
            user: User = google_account.user
            google_account.access_token = tokens["access_token"]
            google_account.refresh_token = tokens.get("refresh_token")
            google_account.token_expires_at = (
                datetime.now(tz=timezone.utc)
                + timedelta(seconds=tokens.get("expires_in", 3600))
                if "expires_in" in tokens
                else None
            )
            google_account.email = email
            google_account.name = name
            google_account.picture = picture
        else:
            # Check if user exists by email
            user_stmt = select(User).where(User.email == email)
            user_result = await transaction.execute(user_stmt)
            existing_user = user_result.scalar_one_or_none()

            if not existing_user:
                # Create new user
                user = User(
                    name=name,
                    email=email,
                    email_verified=True,  # Google emails are verified
                )
                transaction.add(user)
                await transaction.flush()  # To get user.id
            else:
                user = existing_user

            # Create Google OAuth account
            google_account = GoogleOAuthAccount(
                user_id=user.id,
                google_id=google_id,
                email=email,
                name=name,
                picture=picture,
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                token_expires_at=(
                    datetime.now(tz=timezone.utc)
                    + timedelta(seconds=tokens.get("expires_in", 3600))
                    if "expires_in" in tokens
                    else None
                ),
            )
            transaction.add(google_account)

        return user

    async def refresh_access_token(
        self, google_account: GoogleOAuthAccount
    ) -> Optional[str]:
        """Refresh access token using refresh token."""
        if not google_account.refresh_token:
            return None

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": google_account.refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            async with self.http_client.post(self.token_url, data=data) as response:
                response.raise_for_status()
                tokens = await response.json()

            google_account.access_token = tokens["access_token"]
            google_account.token_expires_at = (
                datetime.now(tz=timezone.utc)
                + timedelta(seconds=tokens.get("expires_in", 3600))
                if "expires_in" in tokens
                else None
            )

            # Update refresh token if provided
            if "refresh_token" in tokens:
                google_account.refresh_token = tokens["refresh_token"]

            return tokens["access_token"]
        except Exception:
            return None
