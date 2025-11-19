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
    openai_client = ctx["openai_client"]
    config = ctx["config"]
    queue = ctx["queue"]

    # Step 1: Fetch InboundEmail
    inbound_email_int_id = sqid_decode(inbound_email_id)
    inbound_email = await transaction.get(InboundEmail, inbound_email_int_id)
    if not inbound_email:
        raise ValueError(f"InboundEmail {inbound_email_id} not found")

    # Step 2: Extract attachment metadata
    try:
        s3_key, filename = await get_attachment_s3_key(inbound_email, attachment_index)
    except ValueError:
        logger.warning(f"No attachments found for InboundEmail {inbound_email_id}")
        return {"status": "skipped", "message": "No attachments to process"}

    # Step 2.5: Find user by email and set team context
    if inbound_email.from_email and not inbound_email.team_id:
        from app.users.models import Role

        stmt = select(Role.team_id).join(User).where(User.email == inbound_email.from_email).limit(1)
        result = await transaction.execute(stmt)
        team_id = result.scalar_one_or_none()

        if team_id:
            inbound_email.team_id = team_id
            await transaction.flush()

    # If still no team_id, we can't proceed
    if not inbound_email.team_id:
        raise ValueError(
            f"Cannot determine team_id for InboundEmail {inbound_email_id}. "
            f"User {inbound_email.from_email} not found or has no team."
        )

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
    campaign_link = generate_campaign_link(config.FRONTEND_BASE_URL, campaign_sqid)

    # Step 7: Prepare and enqueue auto-reply email (if from_email exists)
    if inbound_email.from_email:
        email_message_id = await prepare_email_for_queue(
            session=transaction,
            template_name="campaign_created_from_attachment",
            to_email=inbound_email.from_email,
            subject=f"Campaign created: {campaign.name}",
            context={
                "campaign_name": campaign.name,
                "campaign_link": campaign_link,
                "sender_email": inbound_email.from_email,
                "extraction_notes": extraction_result.extraction_notes,
            },
            team_id=inbound_email.team_id,
        )

        await queue.enqueue(
            send_email_task.__name__,
            email_message_id=email_message_id,
        )
        logger.info(f"Enqueued auto-reply email to {inbound_email.from_email} (EmailMessage ID: {email_message_id})")
    else:
        logger.warning(f"Skipping auto-reply email for campaign {campaign_sqid} - no from_email available")

    return {
        "status": "success",
        "campaign_id": campaign_sqid,
        "campaign_name": campaign.name,
        "campaign_link": campaign_link,
        "message": f"Campaign '{campaign.name}' created successfully from {filename}",
    }
