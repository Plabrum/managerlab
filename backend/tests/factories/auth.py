"""Authentication-related model factories."""

from datetime import UTC, datetime, timedelta

from polyfactory import Use

from app.auth.google.models import GoogleOAuthAccount, GoogleOAuthState

from .base import BaseFactory


class GoogleOAuthAccountFactory(BaseFactory):
    """Factory for creating GoogleOAuthAccount instances."""

    __model__ = GoogleOAuthAccount

    google_id = Use(BaseFactory.__faker__.uuid4)
    email = Use(BaseFactory.__faker__.email)
    name = Use(BaseFactory.__faker__.name)
    picture = Use(BaseFactory.__faker__.image_url)
    access_token = Use(BaseFactory.__faker__.sha256)
    refresh_token = Use(BaseFactory.__faker__.sha256)
    token_expires_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="+1h",
        end_date="+1d",
        tzinfo=UTC,
    )
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-6m",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))


class GoogleOAuthStateFactory(BaseFactory):
    """Factory for creating GoogleOAuthState instances."""

    __model__ = GoogleOAuthState

    state = Use(BaseFactory.__faker__.uuid4)
    redirect_uri = Use(BaseFactory.__faker__.url)
    expires_at = Use(lambda: datetime.now(tz=UTC) + timedelta(minutes=10))
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-1h",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))
