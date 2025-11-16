"""Background tasks for campaign processing."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.campaign_decoder import CampaignDecoderAgent
from app.agents.schemas import CampaignExtractionSchema
from app.brands.utils import get_or_create_brand
from app.campaigns.models import Campaign, PaymentBlock
from app.emails.models import InboundEmail
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
    """
    Create a campaign from an inbound email attachment using OpenAI extraction.

    This task:
    1. Fetches the InboundEmail record
    2. Extracts attachment metadata from attachments_json
    3. Runs OpenAI extraction agent
    4. Finds existing brand by name (case-insensitive) or creates new brand
    5. Creates Campaign + PaymentBlocks
    6. Generates campaign link
    7. Enqueues auto-reply email

    Brand Matching Logic:
    - If counterparty_name is extracted, use get_or_create_brand (case-insensitive)
    - Brand creation is required - extraction must provide counterparty_name

    Args:
        ctx: SAQ context with injected dependencies
        transaction: Database session (injected by @with_transaction)
        inbound_email_id: ID of InboundEmail record
        attachment_index: Index of attachment in attachments_json (default: 0)

    Returns:
        Dict with campaign_id, status, and message

    Raises:
        ValueError: If counterparty_name is not extracted
        Exception: On extraction or database failure
    """
    openai_client = ctx["openai_client"]
    config = ctx["config"]
    queue = ctx["queue"]

    # Step 1: Fetch InboundEmail
    inbound_email_int_id = sqid_decode(inbound_email_id)
    inbound_email = await transaction.get(InboundEmail, inbound_email_int_id)
    if not inbound_email:
        raise ValueError(f"InboundEmail {inbound_email_id} not found")

    # Step 2: Extract attachment metadata
    attachments = inbound_email.attachments_json.get("attachments", [])
    if not attachments:
        logger.warning(f"No attachments found for InboundEmail {inbound_email_id}")
        return {"status": "skipped", "message": "No attachments to process"}

    if attachment_index >= len(attachments):
        raise IndexError(f"Attachment index {attachment_index} out of range (max: {len(attachments) - 1})")

    attachment_metadata = attachments[attachment_index]
    s3_key = attachment_metadata["s3_key"]
    filename = attachment_metadata["filename"]

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
    agent = CampaignDecoderAgent(openai_client)
    extraction_result: CampaignExtractionSchema = await agent.run(s3_key=s3_key)
    logger.info(f"Extraction completed: {extraction_result.name} (confidence: {extraction_result.confidence_score})")

    # Step 4: Get or create Brand
    if not extraction_result.counterparty_name:
        raise ValueError(
            f"Extraction failed to provide counterparty_name for {filename}. " "Cannot create campaign without brand."
        )

    brand = await get_or_create_brand(
        session=transaction,
        name=extraction_result.counterparty_name,
        team_id=inbound_email.team_id,
        email=extraction_result.counterparty_email,
    )
    logger.info(f"Using brand: {brand.name} (ID: {brand.id})")

    # Step 5: Create Campaign + PaymentBlocks
    campaign = Campaign(
        name=extraction_result.name,
        description=extraction_result.description,
        team_id=inbound_email.team_id,
        brand_id=brand.id,
        # Counterparty
        counterparty_type=extraction_result.counterparty_type,
        counterparty_name=extraction_result.counterparty_name,
        counterparty_email=extraction_result.counterparty_email,
        # Compensation
        compensation_structure=extraction_result.compensation_structure,
        compensation_total_usd=extraction_result.compensation_total_usd,
        payment_terms_days=extraction_result.payment_terms_days,
        # Flight dates
        flight_start_date=extraction_result.flight_start_date,
        flight_end_date=extraction_result.flight_end_date,
        # FTC & Usage
        ftc_string=extraction_result.ftc_string,
        usage_duration=extraction_result.usage_duration,
        usage_territory=extraction_result.usage_territory,
        usage_paid_media_option=extraction_result.usage_paid_media_option,
        # Exclusivity
        exclusivity_category=extraction_result.exclusivity_category,
        exclusivity_days_before=extraction_result.exclusivity_days_before,
        exclusivity_days_after=extraction_result.exclusivity_days_after,
        # Ownership
        ownership_mode=extraction_result.ownership_mode,
        # Approval
        approval_rounds=extraction_result.approval_rounds,
        approval_sla_hours=extraction_result.approval_sla_hours,
    )

    transaction.add(campaign)
    await transaction.flush()  # Get campaign ID

    # Create payment blocks
    for idx, pb_data in enumerate(extraction_result.payment_blocks):
        payment_block = PaymentBlock(
            campaign_id=campaign.id,
            team_id=inbound_email.team_id,
            label=pb_data.label,
            trigger=pb_data.trigger,
            amount_usd=pb_data.amount_usd,
            percent=pb_data.percent,
            net_days=pb_data.net_days,
            order_index=idx,
        )
        transaction.add(payment_block)

    await transaction.flush()
    campaign_sqid = sqid_encode(campaign.id)
    logger.info(f"Created campaign {campaign_sqid}: {campaign.name}")

    # Step 6: Generate campaign link
    campaign_link = f"{config.FRONTEND_BASE_URL}/campaigns/{campaign_sqid}"

    # Step 7: Enqueue auto-reply email
    await queue.enqueue(
        send_email_task.__name__,
        email_type="campaign_created_from_attachment",
        to_email=inbound_email.from_email,
        context={
            "campaign_name": campaign.name,
            "campaign_link": campaign_link,
            "sender_email": inbound_email.from_email,
            "extraction_notes": extraction_result.extraction_notes,
        },
    )
    logger.info(f"Enqueued auto-reply email to {inbound_email.from_email}")

    return {
        "status": "success",
        "campaign_id": campaign_sqid,
        "campaign_name": campaign.name,
        "campaign_link": campaign_link,
        "message": f"Campaign '{campaign.name}' created successfully from {filename}",
    }
