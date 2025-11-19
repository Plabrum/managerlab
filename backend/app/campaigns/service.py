"""Service layer for campaign creation and management."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.campaign_decoder import CampaignDecoderAgent
from app.agents.schemas import CampaignExtractionSchema
from app.brands.utils import get_or_create_brand
from app.campaigns.models import Campaign, PaymentBlock
from app.client.openai_client import OpenAIClient
from app.emails.models import InboundEmail

logger = logging.getLogger(__name__)


async def extract_campaign_from_s3(
    openai_client: OpenAIClient,
    s3_key: str,
) -> CampaignExtractionSchema:
    """
    Extract campaign data from a PDF file in S3 using OpenAI.

    Args:
        openai_client: OpenAI client instance
        s3_key: S3 key of the PDF file

    Returns:
        CampaignExtractionSchema with extracted data

    Raises:
        Exception: On extraction failure
    """
    logger.info(f"Extracting campaign data from S3 key: {s3_key}")
    agent = CampaignDecoderAgent(openai_client)
    extraction_result = await agent.run(s3_key=s3_key)
    logger.info(
        f"Extraction completed: {extraction_result.name} " f"(confidence: {extraction_result.confidence_score})"
    )
    return extraction_result


async def create_campaign_from_extraction(
    session: AsyncSession,
    extraction: CampaignExtractionSchema,
    team_id: int,
) -> Campaign:
    """
    Create a Campaign and PaymentBlocks from extraction data.

    Args:
        session: Database session
        extraction: Extracted campaign data
        team_id: Team ID for the campaign

    Returns:
        Created Campaign instance (with ID)

    Raises:
        ValueError: If counterparty_name is missing
    """
    # Validate required fields
    if not extraction.counterparty_name:
        raise ValueError("Cannot create campaign without counterparty_name")

    # Get or create brand
    brand = await get_or_create_brand(
        session=session,
        name=extraction.counterparty_name,
        team_id=team_id,
        email=extraction.counterparty_email,
    )
    logger.info(f"Using brand: {brand.name} (ID: {brand.id})")

    # Create campaign
    campaign = Campaign(
        name=extraction.name,
        description=extraction.description,
        team_id=team_id,
        brand_id=brand.id,
        # Counterparty
        counterparty_type=extraction.counterparty_type,
        counterparty_name=extraction.counterparty_name,
        counterparty_email=extraction.counterparty_email,
        # Compensation
        compensation_structure=extraction.compensation_structure,
        compensation_total_usd=extraction.compensation_total_usd,
        payment_terms_days=extraction.payment_terms_days,
        # Flight dates
        flight_start_date=extraction.flight_start_date,
        flight_end_date=extraction.flight_end_date,
        # FTC & Usage
        ftc_string=extraction.ftc_string,
        usage_duration=extraction.usage_duration,
        usage_territory=extraction.usage_territory,
        usage_paid_media_option=extraction.usage_paid_media_option,
        # Exclusivity
        exclusivity_category=extraction.exclusivity_category,
        exclusivity_days_before=extraction.exclusivity_days_before,
        exclusivity_days_after=extraction.exclusivity_days_after,
        # Ownership
        ownership_mode=extraction.ownership_mode,
        # Approval
        approval_rounds=extraction.approval_rounds,
        approval_sla_hours=extraction.approval_sla_hours,
    )

    session.add(campaign)
    await session.flush()  # Get campaign ID

    # Create payment blocks
    for idx, pb_data in enumerate(extraction.payment_blocks):
        payment_block = PaymentBlock(
            campaign_id=campaign.id,
            team_id=team_id,
            label=pb_data.label,
            trigger=pb_data.trigger,
            amount_usd=pb_data.amount_usd,
            percent=pb_data.percent,
            net_days=pb_data.net_days,
            order_index=idx,
        )
        session.add(payment_block)

    await session.flush()
    logger.info(f"Created campaign ID {campaign.id}: {campaign.name}")

    return campaign


async def get_attachment_s3_key(
    inbound_email: InboundEmail,
    attachment_index: int = 0,
) -> tuple[str, str]:
    """
    Get S3 key and filename from inbound email attachment metadata.

    Args:
        inbound_email: InboundEmail instance
        attachment_index: Index of attachment in attachments_json

    Returns:
        Tuple of (s3_key, filename)

    Raises:
        ValueError: If no attachments found
        IndexError: If attachment_index is out of range
    """
    attachments = inbound_email.attachments_json.get("attachments", [])
    if not attachments:
        raise ValueError("No attachments found in inbound email")

    if attachment_index >= len(attachments):
        raise IndexError(f"Attachment index {attachment_index} out of range (max: {len(attachments) - 1})")

    attachment_metadata = attachments[attachment_index]
    s3_key = attachment_metadata["s3_key"]
    filename = attachment_metadata["filename"]

    return s3_key, filename


def generate_campaign_link(frontend_base_url: str, campaign_id: str) -> str:
    """
    Generate frontend link for a campaign.

    Args:
        frontend_base_url: Base URL for frontend
        campaign_id: Campaign ID (sqid)

    Returns:
        Full URL to campaign page
    """
    return f"{frontend_base_url}/campaigns/{campaign_id}"
