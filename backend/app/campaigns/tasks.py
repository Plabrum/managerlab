"""Background tasks for campaign processing."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaigns.service import (
    create_campaign_from_extraction,
    extract_campaign_from_s3,
    generate_campaign_link,
    get_attachment_s3_key,
)
from app.emails.models import InboundEmail
from app.emails.service import prepare_email_for_queue
from app.emails.tasks import send_email_task
from app.queue.registry import task
from app.queue.transactions import with_transaction
from app.queue.types import AppContext
from app.users.models import User
from app.utils.db import get_or_404
from app.utils.sqids import sqid_decode, sqid_encode

logger = logging.getLogger(__name__)


@task
@with_transaction
async def create_campaign_from_attachment_task(
    ctx: AppContext,
    transaction: AsyncSession,
    *,
    inbound_email_id: str,  # Sqid as string
    attachment_index: int = 0,
) -> dict:
    """
    SAQ task to create a campaign from an inbound email attachment.

    Extracts campaign data from a PDF attachment using OpenAI, creates the campaign
    and payment blocks, then sends an auto-reply email to the sender.

    **Prerequisites**: InboundEmail must have valid team_id and from_email (enforced by
    process_inbound_email_task validation and database schema).

    Args:
        ctx: SAQ context with openai_client, config, and queue
        transaction: Database session with active transaction (injected by decorator)
        inbound_email_id: Sqid of the InboundEmail record
        attachment_index: Index of the attachment to process (default: 0)

    Returns:
        dict with campaign details and status
    """
    openai_client = ctx["openai_client"]
    config = ctx["config"]
    queue = ctx["queue"]

    # Step 1: Fetch InboundEmail
    inbound_email_int_id = sqid_decode(inbound_email_id)
    inbound_email = await get_or_404(transaction, InboundEmail, inbound_email_int_id)

    # Step 2: Extract attachment metadata
    try:
        s3_key, filename = await get_attachment_s3_key(inbound_email, attachment_index)
    except ValueError:
        logger.warning(f"No attachments found for InboundEmail {inbound_email_id}")
        return {"status": "skipped", "message": "No attachments to process"}

    # Note: team_id and from_email are guaranteed to be non-null by database schema.
    # Validation happens in process_inbound_email_task before the record is created.

    # Step 3: Run OpenAI extraction agent
    extraction_result = await extract_campaign_from_s3(
        openai_client=openai_client,
        s3_key=s3_key,
    )

    # Step 4 & 5: Create Campaign + PaymentBlocks (includes brand creation)
    campaign = await create_campaign_from_extraction(
        session=transaction,
        extraction=extraction_result,
        team_id=inbound_email.team_id,
    )

    campaign_sqid = sqid_encode(campaign.id)
    logger.info(f"Created campaign {campaign_sqid}: {campaign.name}")

    # Step 6: Generate campaign link
    campaign_link = generate_campaign_link(config.FRONTEND_ORIGIN, campaign_sqid)

    # Step 7: Prepare and enqueue auto-reply email
    # Fetch user to get their name (guaranteed to exist due to validation in process_inbound_email_task)
    stmt = select(User).where(User.email == inbound_email.from_email)
    result = await transaction.execute(stmt)
    user = result.scalar_one()
    user_name = user.name

    email_message_id = await prepare_email_for_queue(
        session=transaction,
        template_name="campaign_created_from_attachment",
        to_email=inbound_email.from_email,
        subject=f"Campaign created: {campaign.name}",
        context={
            "user_name": user_name,
            "campaign_name": campaign.name,
            "campaign_link": campaign_link,
            "sender_email": inbound_email.from_email,
        },
        team_id=inbound_email.team_id,
    )

    await queue.enqueue(
        send_email_task.__name__,
        email_message_id=email_message_id,
    )
    logger.info(f"Enqueued auto-reply email to {inbound_email.from_email} (EmailMessage ID: {email_message_id})")

    return {
        "status": "success",
        "campaign_id": campaign_sqid,
        "campaign_name": campaign.name,
        "campaign_link": campaign_link,
        "message": f"Campaign '{campaign.name}' created successfully from {filename}",
    }
