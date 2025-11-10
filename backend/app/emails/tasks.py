"""Email-related background tasks."""

import logging
from datetime import datetime, timezone

import sqlalchemy as sa

from app.emails.client import EmailMessage as ClientEmailMessage, SESEmailClient
from app.emails.enums import EmailState
from app.emails.models import EmailMessage
from app.queue.registry import task
from app.queue.types import AppContext

logger = logging.getLogger(__name__)


@task
async def send_email_task(ctx: AppContext, *, email_message_id: int) -> dict:
    """
    SAQ task to send an email via SES.

    Args:
        ctx: SAQ context with db_sessionmaker and config
        email_message_id: ID of EmailMessage to send

    Returns:
        dict with status and message_id
    """
    db_sessionmaker = ctx["db_sessionmaker"]
    config = ctx["config"]

    async with db_sessionmaker() as db_session:
        # Fetch email from database
        stmt = sa.select(EmailMessage).where(EmailMessage.id == email_message_id)
        result = await db_session.execute(stmt)
        email = result.scalar_one()

        try:
            # Create SES client
            ses_client = SESEmailClient(config)

            # Build message
            message = ClientEmailMessage(
                to=email.to_email.split(","),  # Handle comma-separated emails
                subject=email.subject,
                body_html=email.body_html,
                body_text=email.body_text,
                from_email=email.from_email,
                reply_to=email.reply_to_email,
            )

            # Send via SES
            ses_message_id = await ses_client.send_email(message)

            # Update database
            email.state = EmailState.SENT
            email.ses_message_id = ses_message_id
            email.sent_at = datetime.now(timezone.utc)
            await db_session.commit()

            logger.info(f"Email {email_message_id} sent: {ses_message_id}")

            return {
                "status": "sent",
                "email_id": email_message_id,
                "ses_message_id": ses_message_id,
            }

        except Exception as e:
            # Mark as failed
            email.state = EmailState.FAILED
            email.error_message = str(e)
            await db_session.commit()

            logger.error(f"Failed to send email {email_message_id}: {e}")
            raise
