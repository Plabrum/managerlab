"""Background tasks for campaign processing."""

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.campaign_decoder import campaign_decoder_agent
from app.agents.schemas import CampaignExtractionSchema
from app.campaigns.models import Campaign, PaymentBlock
from app.emails.models import InboundEmail
from app.emails.tasks import send_email_task
from app.queue.registry import task
from app.queue.transactions import with_transaction
from app.queue.types import AppContext
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
    3. Downloads attachment from S3
    4. Runs OpenAI extraction agent
    5. Creates Campaign + PaymentBlocks
    6. Generates campaign link
    7. Enqueues auto-reply email

    Args:
        ctx: SAQ context with injected dependencies
        transaction: Database session (injected by @with_transaction)
        inbound_email_id: ID of InboundEmail record
        attachment_index: Index of attachment in attachments_json (default: 0)

    Returns:
        Dict with campaign_id, status, and message
    """
    s3_client = ctx["s3_client"]
    openai_client = ctx["openai_client"]
    config = ctx["config"]
    task_queues = ctx.get("task_queues")

    # Step 1: Fetch InboundEmail
    inbound_email_int_id = sqid_decode(inbound_email_id)
    inbound_email = await transaction.get(InboundEmail, inbound_email_int_id)
    if not inbound_email:
        error_msg = f"InboundEmail {inbound_email_id} not found"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    # Step 2: Extract attachment metadata
    try:
        # Handle attachments_json which can be dict or None
        attachments_data = inbound_email.attachments_json
        if attachments_data is None:
            attachments = []
        elif isinstance(attachments_data, dict):
            attachments = attachments_data.get("attachments", [])
        else:
            attachments = json.loads(attachments_data) if isinstance(attachments_data, str) else []
        if not attachments:
            logger.warning(f"No attachments found for InboundEmail {inbound_email_id}")
            return {"status": "skipped", "message": "No attachments to process"}

        if attachment_index >= len(attachments):
            error_msg = f"Attachment index {attachment_index} out of range (max: {len(attachments) - 1})"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

        attachment_metadata = attachments[attachment_index]
        s3_key = attachment_metadata["s3_key"]
        filename = attachment_metadata["filename"]

    except (json.JSONDecodeError, KeyError) as e:
        error_msg = f"Failed to parse attachment metadata: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    # Step 3: Download attachment from S3
    try:
        file_bytes = s3_client.get_file_bytes(s3_key)
        logger.info(f"Downloaded attachment {filename} ({len(file_bytes)} bytes)")
    except Exception as e:
        error_msg = f"Failed to download attachment from S3: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    # Step 4: Run OpenAI extraction agent
    try:
        extraction_result: CampaignExtractionSchema = await campaign_decoder_agent.run(
            file_bytes=file_bytes,
            filename=filename,
            openai_client=openai_client,
        )
        logger.info(
            f"Extraction completed: {extraction_result.name} (confidence: {extraction_result.confidence_score})"
        )
    except Exception as e:
        error_msg = f"OpenAI extraction failed: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    # Step 5: Create Campaign + PaymentBlocks
    try:
        # Create campaign from extraction data
        campaign = Campaign(
            name=extraction_result.name,
            description=extraction_result.description,
            team_id=inbound_email.team_id,
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

    except Exception as e:
        error_msg = f"Failed to create campaign: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    # Step 6: Generate campaign link
    campaign_link = f"{config.FRONTEND_BASE_URL}/campaigns/{campaign_sqid}"

    # Step 7: Enqueue auto-reply email
    # Note: We'll implement the email template next, but enqueue the task now
    try:
        if task_queues:
            queue = task_queues.get("default")
            await queue.enqueue(
                send_email_task,
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
    except Exception as e:
        logger.warning(f"Failed to enqueue auto-reply email: {e}")
        # Don't fail the task if email fails - campaign is already created

    return {
        "status": "success",
        "campaign_id": campaign_sqid,
        "campaign_name": campaign.name,
        "campaign_link": campaign_link,
        "message": f"Campaign '{campaign.name}' created successfully from {filename}",
    }
