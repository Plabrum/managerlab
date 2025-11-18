"""Email service with template rendering."""

from pathlib import Path
from typing import Any

from email_validator import EmailNotValidError, validate_email
from jinja2 import Environment, FileSystemLoader
from litestar.contrib.jinja import JinjaTemplateEngine
from sqlalchemy.ext.asyncio import AsyncSession

from app.emails.client import BaseEmailClient, EmailMessage as ClientEmailMessage
from app.emails.models import EmailMessage as DBEmailMessage
from app.utils.configure import config


class EmailService:
    """High-level email service with template rendering."""

    def __init__(
        self,
        email_client: BaseEmailClient,
        template_engine: JinjaTemplateEngine,
    ):
        self.client = email_client
        self.config = config
        self.template_engine = template_engine

    def validate_email_address(self, email: str) -> str:
        """Validate and normalize email address."""
        try:
            valid = validate_email(email, check_deliverability=False)
            return valid.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {email}") from e

    def render_template(self, template_name: str, context: dict[str, Any]) -> tuple[str, str]:
        """Render email template to HTML and plain text."""
        # Access the underlying Jinja2 environment
        jinja_env = self.template_engine.engine

        # Render HTML template
        html_template_path = f"{template_name}/html.jinja2"
        html_template = jinja_env.get_template(html_template_path)
        html_body = html_template.render(**context)

        # Render text template
        text_template_path = f"{template_name}/text.jinja2"
        text_template = jinja_env.get_template(text_template_path)
        text_body = text_template.render(**context)

        return html_body, text_body

    async def send_email(
        self,
        to: list[str] | str,
        subject: str,
        template_name: str,
        context: dict[str, Any],
        from_email: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
    ) -> str:
        """Send an email using a template."""
        # Normalize recipients
        if isinstance(to, str):
            to = [to]

        # Validate all email addresses
        to = [self.validate_email_address(email) for email in to]

        # Use default from email/name if not specified
        if not from_email:
            from_email = self.config.SES_FROM_EMAIL
        if not from_name:
            from_name = self.config.SES_FROM_NAME

        # Render template
        html_body, text_body = self.render_template(template_name, context)

        # Create message
        message = ClientEmailMessage(
            to=to,
            subject=subject,
            body_html=html_body,
            body_text=text_body,
            from_email=from_email,
            from_name=from_name,
            reply_to=reply_to or self.config.SES_REPLY_TO_EMAIL,
        )

        # Send via client
        return await self.client.send_email(message)

    async def send_magic_link_email(
        self,
        to_email: str,
        magic_link_url: str,
        expires_minutes: int = 15,
    ) -> str:
        """Send magic link login email."""
        context = {
            "magic_link_url": magic_link_url,
            "user_email": to_email,
            "expiration_minutes": expires_minutes,  # React Email template uses expiration_minutes
        }

        return await self.send_email(
            to=to_email,
            subject="Sign in to Arive",
            template_name="magic_link",
            context=context,
        )

    async def send_team_invitation_email(
        self,
        to_email: str,
        team_name: str,
        inviter_name: str,
        invitation_link: str,
        expires_hours: int = 72,
    ) -> str:
        """Send team invitation email."""
        context = {
            "invitee_email": to_email,
            "team_name": team_name,
            "inviter_name": inviter_name,
            "invitation_url": invitation_link,  # React Email template uses invitation_url
            "expiration_hours": expires_hours,  # React Email template uses expiration_hours
        }

        return await self.send_email(
            to=to_email,
            subject=f"You're invited to join {team_name} on Arive",
            template_name="team_invitation",
            context=context,
        )


async def prepare_email_for_queue(
    session: AsyncSession,
    *,
    template_name: str,
    to_email: str,
    subject: str,
    context: dict[str, Any],
    team_id: int,
    from_email: str | None = None,
    reply_to_email: str | None = None,
) -> int:
    """
    Prepare an email for background sending via queue.

    This function renders an email template and creates an EmailMessage record
    that can be sent later via the send_email_task background task.

    Use this from background tasks that don't have access to EmailService.

    Args:
        session: Database session
        template_name: Name of email template (e.g., "magic_link", "team_invitation")
        to_email: Recipient email address
        subject: Email subject line
        context: Template context variables
        team_id: Team ID for RLS
        from_email: Optional sender email (defaults to config.SES_FROM_EMAIL)
        reply_to_email: Optional reply-to email (defaults to config.SES_REPLY_TO_EMAIL)

    Returns:
        EmailMessage ID that can be passed to send_email_task
    """
    # Set up Jinja2 environment for template rendering
    templates_dir = Path(__file__).parent.parent.parent / "templates" / "emails-react"
    jinja_env = Environment(loader=FileSystemLoader(templates_dir))

    # Render HTML template
    html_template = jinja_env.get_template(f"{template_name}/html.jinja2")
    html_body = html_template.render(**context)

    # Render text template
    text_template = jinja_env.get_template(f"{template_name}/text.jinja2")
    text_body = text_template.render(**context)

    # Use config defaults if not provided
    from_email = from_email or config.SES_FROM_EMAIL
    reply_to_email = reply_to_email or config.SES_REPLY_TO_EMAIL

    # Create EmailMessage record
    email_message = DBEmailMessage(
        to_email=to_email,
        from_email=from_email,
        reply_to_email=reply_to_email,
        subject=subject,
        body_html=html_body,
        body_text=text_body,
        template_name=template_name,
        team_id=team_id,
    )

    session.add(email_message)
    await session.flush()

    return email_message.id
