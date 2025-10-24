from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaigns.models import Campaign
from app.campaigns.schemas import CampaignSchema, CampaignUpdateSchema
from app.utils.sqids import Sqid
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model
from app.actions.registry import ActionRegistry
from app.actions.enums import ActionGroupType

# Register CampaignObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.campaigns.objects import CampaignObject

ObjectRegistry().register(ObjectTypes.Campaigns, CampaignObject)


@get("/{id:str}")
async def get_campaign(
    id: Sqid, transaction: AsyncSession, action_registry: ActionRegistry
) -> CampaignSchema:
    """Get a campaign by SQID."""
    campaign = await get_or_404(transaction, Campaign, id)

    # Compute actions for this campaign
    action_group = action_registry.get_class(ActionGroupType.CampaignActions)
    actions = action_group.get_available_actions(obj=campaign)

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
    )


@post("/{id:str}")
async def update_campaign(
    id: Sqid, data: CampaignUpdateSchema, transaction: AsyncSession
) -> CampaignSchema:
    """Update a campaign by SQID."""
    campaign = await get_or_404(transaction, Campaign, id)
    update_model(campaign, data)
    await transaction.flush()
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


campaign_router = Router(
    path="/campaigns",
    guards=[requires_user_id],
    route_handlers=[
        get_campaign,
        update_campaign,
    ],
    tags=["campaigns"],
)
