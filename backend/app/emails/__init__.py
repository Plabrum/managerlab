"""Email module for sending emails via AWS SES."""

from app.emails.client import BaseEmailClient, LocalEmailClient, SESEmailClient
from app.emails.service import EmailService

__all__ = ["BaseEmailClient", "LocalEmailClient", "SESEmailClient", "EmailService"]
