"""Email client abstraction for local development and AWS SES."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Annotated

from litestar.params import Dependency

from app.utils.configure import Config

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Email message data."""

    to: list[str]
    subject: str
    body_html: str
    body_text: str
    from_email: str
    reply_to: str | None = None


class BaseEmailClient(ABC):
    """Abstract base class for email clients."""

    @abstractmethod
    async def send_email(self, message: EmailMessage) -> str:
        """Send an email. Returns message ID."""
        pass


class LocalEmailClient(BaseEmailClient):
    """Local email client that logs to console (for development)."""

    async def send_email(self, message: EmailMessage) -> str:
        """Log email instead of sending."""
        logger.info("=" * 80)
        logger.info("LOCAL EMAIL (not actually sent)")
        logger.info(f"To: {', '.join(message.to)}")
        logger.info(f"From: {message.from_email}")
        logger.info(f"Subject: {message.subject}")
        logger.info(f"Reply-To: {message.reply_to}")
        logger.info("-" * 80)
        logger.info(f"HTML Body:\n{message.body_html}")
        logger.info("-" * 80)
        logger.info(f"Text Body:\n{message.body_text}")
        logger.info("=" * 80)

        return f"local-{hash(message.subject)}"


class SESEmailClient(BaseEmailClient):
    """AWS SES email client (async)."""

    def __init__(self, config: Config):
        self.region = config.SES_REGION
        self.configuration_set = config.SES_CONFIGURATION_SET

    async def send_email(self, message: EmailMessage) -> str:
        """Send email via AWS SES."""
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        import aioboto3

        session = aioboto3.Session()

        async with session.client("ses", region_name=self.region) as ses:
            # Build MIME message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = message.from_email
            msg["To"] = ", ".join(message.to)

            if message.reply_to:
                msg["Reply-To"] = message.reply_to

            # Add text and HTML parts
            msg.attach(MIMEText(message.body_text, "plain", "utf-8"))
            msg.attach(MIMEText(message.body_html, "html", "utf-8"))

            # Send via SES
            kwargs = {
                "Source": message.from_email,
                "Destinations": message.to,
                "RawMessage": {"Data": msg.as_string()},
            }

            if self.configuration_set:
                kwargs["ConfigurationSetName"] = self.configuration_set

            response = await ses.send_raw_email(**kwargs)

            logger.info(f"Email sent via SES: {response['MessageId']}")
            return response["MessageId"]


def provide_email_client(config: Config) -> BaseEmailClient:
    """Factory function to create appropriate email client based on config."""
    if config.IS_DEV:
        return LocalEmailClient()
    else:
        return SESEmailClient(config)


EmailClientDep = Annotated[BaseEmailClient, Dependency()]
