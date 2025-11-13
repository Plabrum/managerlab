"""Dependency injection for email module."""

from litestar.template import TemplateEngineProtocol

from app.emails.client import BaseEmailClient, provide_email_client
from app.emails.service import EmailService


def provide_email_service(
    email_client: BaseEmailClient,
    template_engine: TemplateEngineProtocol,
) -> EmailService:
    """Factory for email service."""
    return EmailService(email_client, template_engine)


# Re-export for convenience
__all__ = ["provide_email_client", "provide_email_service"]
