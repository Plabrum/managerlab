"""Email-related background tasks."""

import logging
from datetime import UTC, datetime
from email import message_from_bytes
from email.utils import parsedate_to_datetime
from io import BytesIO

import sqlalchemy as sa

from app.emails.client import EmailMessage as ClientEmailMessage, SESEmailClient
from app.emails.models import EmailMessage, InboundEmail
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
            email.ses_message_id = ses_message_id
            email.sent_at = datetime.now(UTC)
            await db_session.commit()

            logger.info(f"Email {email_message_id} sent: {ses_message_id}")

            return {
                "status": "sent",
                "email_id": email_message_id,
                "ses_message_id": ses_message_id,
            }

        except Exception as e:
            # Mark as failed
            email.error_message = str(e)
            await db_session.commit()

            logger.error(f"Failed to send email {email_message_id}: {e}")
            raise


@task
async def process_inbound_email_task(ctx: AppContext, *, bucket: str, key: str) -> dict:
    """
    SAQ task to process an inbound email from S3.

    Creates InboundEmail record, fetches raw email from S3, parses headers and metadata,
    extracts attachments and stores them in S3.

    Args:
        ctx: SAQ context with db_sessionmaker, s3_client, and config
        bucket: S3 bucket containing the email
        key: S3 key of the email file

    Returns:
        dict with status and processing details
    """
    db_sessionmaker = ctx["db_sessionmaker"]
    s3_client = ctx["s3_client"]

    async with db_sessionmaker() as db_session:
        # Create InboundEmail record
        inbound = InboundEmail(
            s3_bucket=bucket,
            s3_key=key,
            team_id=None,  # Matched later if needed
        )
        db_session.add(inbound)
        await db_session.flush()  # Get the ID assigned

        try:
            # Store task ID for status tracking
            job = ctx.get("job")
            if job:
                inbound.task_id = job.key

            await db_session.commit()

            # Fetch raw email from S3
            logger.info(f"Fetching email from s3://{bucket}/{key}")
            email_bytes = s3_client.get_file_bytes(inbound.s3_key)

            # Parse MIME message
            msg = message_from_bytes(email_bytes)

            # Extract and store metadata from headers
            inbound.from_email = msg.get("From", "unknown@unknown.com")
            inbound.to_email = msg.get("To", "unknown@unknown.com")
            inbound.subject = msg.get("Subject", "(no subject)")
            inbound.ses_message_id = msg.get("Message-ID", f"local-{inbound.id}")

            # Parse received timestamp if available
            date_str = msg.get("Date")
            if date_str:
                try:
                    inbound.received_at = parsedate_to_datetime(date_str)
                except Exception as date_error:
                    logger.warning(f"Failed to parse date '{date_str}': {date_error}")

            await db_session.commit()

            logger.info(f"Processing email from {inbound.from_email}")
            logger.info(f"Subject: {inbound.subject}")

            # Extract attachments
            attachments = []
            for part in msg.walk():
                # Check if this is an attachment
                if part.get_content_disposition() == "attachment":
                    filename = part.get_filename()
                    if not filename:
                        continue

                    # Get attachment data
                    attachment_data = part.get_payload(decode=True)
                    if not attachment_data or not isinstance(attachment_data, bytes):
                        continue

                    # Generate S3 key for attachment
                    s3_key = f"emails/attachments/{inbound.id}/{filename}"

                    # Upload to S3
                    logger.info(f"Uploading attachment: {filename} ({len(attachment_data)} bytes)")
                    s3_client.upload_fileobj(BytesIO(attachment_data), s3_key)

                    # Store metadata
                    attachments.append(
                        {
                            "filename": filename,
                            "s3_key": s3_key,
                            "content_type": part.get_content_type(),
                            "size": len(attachment_data),
                        }
                    )

            # Save attachments metadata
            if attachments:
                inbound.attachments_json = {"attachments": attachments}
                logger.info(f"Extracted {len(attachments)} attachment(s)")

            # Mark as processed
            inbound.processed_at = datetime.now(UTC)
            await db_session.commit()

            return {
                "status": "processed",
                "inbound_email_id": inbound.id,
                "from": inbound.from_email,
                "subject": inbound.subject,
                "attachment_count": len(attachments),
            }

        except Exception as e:
            # Mark as failed
            inbound.error_message = str(e)
            await db_session.commit()

            logger.error(f"Failed to process inbound email {inbound.id}: {e}")
            raise
