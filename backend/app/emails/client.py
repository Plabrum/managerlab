"""Email client abstraction for local development and AWS SES."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated

import aioboto3
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
    from_name: str | None = None
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
        # Format From header with display name if provided
        from_header = f'"{message.from_name}" <{message.from_email}>' if message.from_name else message.from_email

        logger.info("=" * 80)
        logger.info("LOCAL EMAIL (not actually sent)")
        logger.info(f"To: {', '.join(message.to)}")
        logger.info(f"From: {from_header}")
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

        session = aioboto3.Session()

        async with session.client("ses", region_name=self.region) as ses:
            # Format From header with display name if provided
            from_header = f'"{message.from_name}" <{message.from_email}>' if message.from_name else message.from_email

            # Build MIME message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = from_header  # Can include display name
            msg["To"] = ", ".join(message.to)

            if message.reply_to:
                msg["Reply-To"] = message.reply_to

            # Add text and HTML parts
            msg.attach(MIMEText(message.body_text, "plain", "utf-8"))
            msg.attach(MIMEText(message.body_html, "html", "utf-8"))

            # Send via SES
            kwargs = {
                "Source": message.from_email,  # Must be just the email address
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
    if config.ALLOW_LOCAL_SES or not config.IS_DEV:
        return SESEmailClient(config)
    else:
        return LocalEmailClient()


EmailClientDep = Annotated[BaseEmailClient, Dependency()]
