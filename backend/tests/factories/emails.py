"""Email-related model factories."""

from datetime import UTC, datetime

from polyfactory import Use

from app.emails.models import InboundEmail

from .base import BaseFactory


class InboundEmailFactory(BaseFactory):
    """Factory for creating InboundEmail instances."""

    __model__ = InboundEmail

    s3_bucket = "test-inbound-emails-bucket"
    s3_key = Use(lambda: f"emails/{BaseFactory.__faker__.uuid4()}.eml")
    from_email = Use(BaseFactory.__faker__.email)
    to_email = "contracts@tryarive.com"
    subject = Use(BaseFactory.__faker__.sentence)
    ses_message_id = Use(lambda: f"<{BaseFactory.__faker__.uuid4()}@email.amazonses.com>")
    received_at = Use(lambda: datetime.now(tz=UTC))
    attachments_json = None
    processed_at = None
    error_message = None
    team_id = None
    task_id = None
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-30d",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))
    deleted_at = None
