from litestar import Request, Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.agents.schemas import ExtractFromContractRequestSchema, ExtractFromContractResponseSchema
from app.auth.guards import requires_session
from app.campaigns.models import Campaign
from app.campaigns.schemas import CampaignSchema, CampaignUpdateSchema
from app.client.openai_client import OpenAIClient
from app.client.s3_client import BaseS3Client
from app.documents.models import Document
from app.threads.models import Thread
from app.utils.db import get_or_404, update_model
from app.utils.sqids import Sqid


@get("/{id:str}")
async def get_campaign(
    id: Sqid,
    request: Request,
    transaction: AsyncSession,
    action_registry: ActionRegistry,
) -> CampaignSchema:
    campaign = await get_or_404(
        transaction,
        Campaign,
        id,
        load_options=[
            joinedload(Campaign.thread).options(
                selectinload(Thread.messages),
                selectinload(Thread.read_statuses),
            ),
            joinedload(Campaign.contract),
            selectinload(Campaign.contract_versions),
        ],
    )

    # Compute actions for this campaign
    action_group = action_registry.get_class(ActionGroupType.CampaignActions)
    actions = action_group.get_available_actions(obj=campaign)

    # Convert thread to unread info using the mixin method
    thread_info = campaign.get_thread_unread_info(request.user)

    return CampaignSchema(
        id=campaign.id,
        name=campaign.name,
        description=campaign.description,
        compensation_structure=campaign.compensation_structure,
        assigned_roster_id=campaign.assigned_roster_id,
        brand_id=campaign.brand_id,
        state=campaign.state,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        team_id=campaign.team_id,
        actions=actions,
        # Counterparty
        counterparty_type=campaign.counterparty_type,
        counterparty_name=campaign.counterparty_name,
        counterparty_email=campaign.counterparty_email,
        # Compensation
        compensation_total_usd=campaign.compensation_total_usd,
        payment_terms_days=campaign.payment_terms_days,
        # Flight dates
        flight_start_date=campaign.flight_start_date,  # type: ignore
        flight_end_date=campaign.flight_end_date,  # type: ignore
        # FTC & Usage
        ftc_string=campaign.ftc_string,
        usage_duration=campaign.usage_duration,
        usage_territory=campaign.usage_territory,
        usage_paid_media_option=campaign.usage_paid_media_option,
        # Exclusivity
        exclusivity_category=campaign.exclusivity_category,
        exclusivity_days_before=campaign.exclusivity_days_before,
        exclusivity_days_after=campaign.exclusivity_days_after,
        # Ownership
        ownership_mode=campaign.ownership_mode,
        # Approval
        approval_rounds=campaign.approval_rounds,
        approval_sla_hours=campaign.approval_sla_hours,
        thread=thread_info,
    )


@post("/{id:str}")
async def update_campaign(
    id: Sqid, data: CampaignUpdateSchema, request: Request, transaction: AsyncSession
) -> CampaignSchema:
    """Update a campaign by SQID."""
    campaign = await get_or_404(transaction, Campaign, id)
    await update_model(
        session=transaction,
        model_instance=campaign,
        update_vals=data,
        user_id=request.user,
        team_id=campaign.team_id,
    )
    return CampaignSchema(
        id=campaign.id,
        name=campaign.name,
        description=campaign.description,
        compensation_structure=campaign.compensation_structure,
        assigned_roster_id=campaign.assigned_roster_id,
        brand_id=campaign.brand_id,
        state=campaign.state,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        team_id=campaign.team_id,
        actions=[],  # Update endpoints don't compute actions
        # Counterparty
        counterparty_type=campaign.counterparty_type,
        counterparty_name=campaign.counterparty_name,
        counterparty_email=campaign.counterparty_email,
        # Compensation
        compensation_total_usd=campaign.compensation_total_usd,
        payment_terms_days=campaign.payment_terms_days,
        # Flight dates
        flight_start_date=campaign.flight_start_date,  # type: ignore
        flight_end_date=campaign.flight_end_date,  # type: ignore
        # FTC & Usage
        ftc_string=campaign.ftc_string,
        usage_duration=campaign.usage_duration,
        usage_territory=campaign.usage_territory,
        usage_paid_media_option=campaign.usage_paid_media_option,
        # Exclusivity
        exclusivity_category=campaign.exclusivity_category,
        exclusivity_days_before=campaign.exclusivity_days_before,
        exclusivity_days_after=campaign.exclusivity_days_after,
        # Ownership
        ownership_mode=campaign.ownership_mode,
        # Approval
        approval_rounds=campaign.approval_rounds,
        approval_sla_hours=campaign.approval_sla_hours,
    )


@post("/extract-from-contract")
async def extract_from_contract(
    data: ExtractFromContractRequestSchema,
    request: Request,
    transaction: AsyncSession,
    s3_client: BaseS3Client,
    openai_client: OpenAIClient,
) -> ExtractFromContractResponseSchema:
    """
    Extract structured campaign data from a contract document using OpenAI agent.

    This endpoint:
    1. Fetches the document by ID (with team access validation via RLS)
    2. Downloads file from S3
    3. Runs OpenAI extraction agent
    4. Returns structured campaign data for form pre-fill

    Args:
        data: Request with document_id
        request: Litestar request (for user context)
        transaction: Database session
        s3_client: S3 client for file download
        openai_client: OpenAI client for extraction

    Returns:
        ExtractFromContractResponseSchema with extracted campaign data
    """
    # Fetch document - RLS will ensure user has access
    from app.agents.campaign_decoder import CampaignDecoderAgent
    from app.utils.sqids import sqid_decode

    document = await get_or_404(transaction, Document, sqid_decode(data.document_id))

    # Create agent with injected OpenAI client
    agent = CampaignDecoderAgent(openai_client)

    # Run extraction agent (handles S3 download and OpenAI file cleanup internally)
    extraction_result = await agent.run(s3_key=document.file_key)

    return ExtractFromContractResponseSchema(
        data=extraction_result,
        message=f"Successfully extracted campaign data from {document.file_name}",
    )


campaign_router = Router(
    path="/campaigns",
    guards=[requires_session],
    route_handlers=[
        get_campaign,
        update_campaign,
        extract_from_contract,
    ],
    tags=["campaigns"],
)
