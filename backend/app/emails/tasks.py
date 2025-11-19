"""Email-related background tasks."""

import logging
from datetime import UTC, datetime
from email import message_from_bytes
from email.utils import parsedate_to_datetime
from io import BytesIO

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.emails.client import EmailMessage as ClientEmailMessage, SESEmailClient
from app.emails.models import EmailMessage, InboundEmail
from app.queue.registry import task
from app.queue.transactions import with_transaction
from app.queue.types import AppContext

logger = logging.getLogger(__name__)


@task
@with_transaction
async def send_email_task(
    ctx: AppContext,
    transaction: AsyncSession,
    *,
    email_message_id: int,
) -> dict:
    """
    SAQ task to send an email via SES.

    Args:
        ctx: SAQ context with db_sessionmaker and config
        transaction: Database session with active transaction (injected by decorator)
        email_message_id: ID of EmailMessage to send

    Returns:
        dict with status and message_id
    """
    config = ctx["config"]

    # Fetch email from database
    stmt = sa.select(EmailMessage).where(EmailMessage.id == email_message_id)
    result = await transaction.execute(stmt)
    email = result.scalar_one()

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
    # Auto-commit happens via decorator

    logger.info(f"Email {email_message_id} sent: {ses_message_id}")

    return {
        "status": "sent",
        "email_id": email_message_id,
        "ses_message_id": ses_message_id,
    }


@task
@with_transaction
async def process_inbound_email_task(
    ctx: AppContext,
    transaction: AsyncSession,
    *,
    bucket: str,
    s3_key: str,
) -> dict:
    """
    SAQ task to process an inbound email from S3.

    Fetches raw email from S3, parses headers and metadata, extracts attachments,
    then atomically creates InboundEmail record with all data.

    Args:
        ctx: SAQ context with db_sessionmaker, s3_client, and config
        transaction: Database session with active transaction (injected by decorator)
        bucket: S3 bucket containing the email
        s3_key: S3 key of the email file

    Returns:
        dict with status and processing details
    """
    s3_client = ctx["s3_client"]

    # Phase 1: Fetch and parse email from S3 (no database interaction)
    logger.info(f"Fetching email from s3://{bucket}/{s3_key}")
    email_bytes = s3_client.get_file_bytes_from_bucket(bucket, s3_key)

    # Parse MIME message
    msg = message_from_bytes(email_bytes)

    # Extract metadata from headers
    from_email = msg.get("From", "unknown@unknown.com")
    to_email = msg.get("To", "unknown@unknown.com")
    subject = msg.get("Subject", "(no subject)")
    message_id = msg.get("Message-ID")

    # Parse received timestamp if available
    received_at = datetime.now(UTC)
    date_str = msg.get("Date")
    if date_str:
        try:
            received_at = parsedate_to_datetime(date_str)
        except Exception as date_error:
            logger.warning(f"Failed to parse date '{date_str}': {date_error}")

    logger.info(f"Processing email from {from_email}")
    logger.info(f"Subject: {subject}")

    # Extract attachment data (in memory, not uploaded yet)
    attachment_parts = []
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if not filename:
                continue

            attachment_data = part.get_payload(decode=True)
            if not attachment_data or not isinstance(attachment_data, bytes):
                continue

            attachment_parts.append(
                {
                    "filename": filename,
                    "data": attachment_data,
                    "content_type": part.get_content_type(),
                }
            )

    # Phase 2: Create record and upload attachments (auto-wrapped in transaction)
    # Store task ID for status tracking
    job = ctx.get("job")
    task_id = job.key if job else None

    # Insert with on_conflict_do_nothing - database handles duplicates atomically
    stmt = (
        insert(InboundEmail)
        .values(
            s3_bucket=bucket,
            s3_key=s3_key,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            ses_message_id=message_id,
            received_at=received_at,
            processed_at=datetime.now(UTC),
            team_id=None,  # Matched later if needed
            task_id=task_id,
            attachments_json={"attachments": []},  # Initialize empty, populated later if attachments exist
        )
        .on_conflict_do_nothing(index_elements=["s3_key"])
        .returning(InboundEmail)
    )

    result = await transaction.execute(stmt)
    inbound = result.scalar_one_or_none()

    if inbound is None:
        # Conflict occurred - record already exists, skip attachment processing
        stmt = sa.select(InboundEmail).where(InboundEmail.s3_key == s3_key)
        result = await transaction.execute(stmt)
        existing = result.scalar_one()

        logger.info(f"Email already processed: {s3_key} (id={existing.id})")
        return {
            "status": "processed",
            "inbound_email_id": existing.id,
            "from": from_email,
            "subject": subject,
            "attachment_count": (
                len(existing.attachments_json.get("attachments", [])) if existing.attachments_json else 0
            ),
        }

    # Now upload attachments with the DB ID
    attachments_metadata = []
    for attachment in attachment_parts:
        # Generate S3 key using the record ID
        attachment_s3_key = f"emails/attachments/{inbound.id}/{attachment['filename']}"

        # Upload to S3
        logger.info(f"Uploading attachment: {attachment['filename']} ({len(attachment['data'])} bytes)")
        s3_client.upload_fileobj(BytesIO(attachment["data"]), attachment_s3_key)

        # Store metadata
        attachments_metadata.append(
            {
                "filename": attachment["filename"],
                "s3_key": attachment_s3_key,
                "content_type": attachment["content_type"],
                "size": len(attachment["data"]),
            }
        )

    # Save attachments metadata
    if attachments_metadata:
        inbound.attachments_json = {"attachments": attachments_metadata}
        logger.info(f"Extracted {len(attachments_metadata)} attachment(s)")

    # Set final message_id with fallback to local ID
    if not inbound.ses_message_id:
        inbound.ses_message_id = f"local-{inbound.id}"

    # Phase 3: Enqueue campaign creation for attachments (if any)
    from app.utils.sqids import sqid_encode

    if attachments_metadata:
        from app.campaigns.tasks import create_campaign_from_attachment_task

        queue = ctx["queue"]
        inbound_sqid = sqid_encode(inbound.id)

        # Enqueue campaign creation task for first attachment
        # (You could process all attachments by looping here)
        try:
            await queue.enqueue(
                create_campaign_from_attachment_task.__name__,
                inbound_email_id=inbound_sqid,
                attachment_index=0,
            )
            logger.info(f"Enqueued campaign creation task for InboundEmail {inbound_sqid}")
        except Exception as enqueue_error:
            logger.warning(f"Failed to enqueue campaign creation task: {enqueue_error}")
            # Don't fail the task - email is already processed

    # Transaction auto-commits here with complete record

    return {
        "status": "processed",
        "inbound_email_id": inbound.id,
        "from": from_email,
        "subject": subject,
        "attachment_count": len(attachments_metadata),
    }
