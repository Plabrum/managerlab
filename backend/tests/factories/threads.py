"""Thread-related model factories."""

from datetime import UTC, datetime

from polyfactory import Use

from app.threads.models import Message, Thread

from .base import BaseFactory


class ThreadFactory(BaseFactory):
    """Factory for creating Thread instances."""

    __model__ = Thread

    threadable_type = "Campaign"  # Default to Campaign, override as needed
    threadable_id = 1  # Must be explicitly set to valid ID
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-1y",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))
    deleted_at = None


class MessageFactory(BaseFactory):
    """Factory for creating Message instances."""

    __model__ = Message

    content = Use(
        lambda: {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": BaseFactory.__faker__.sentence()}],
                }
            ],
        }
    )
    campaign_id = None  # Must be explicitly set if needed
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-1y",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))
    deleted_at = None
