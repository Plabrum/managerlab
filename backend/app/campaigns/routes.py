from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaigns.models import Campaign
from app.campaigns.schemas import CampaignSchema, CampaignUpdateSchema
from app.utils.sqids import Sqid
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model

# Register CampaignObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.campaigns.objects import CampaignObject

ObjectRegistry().register(ObjectTypes.Campaigns, CampaignObject)


@get("/{id:str}")
async def get_campaign(id: Sqid, transaction: AsyncSession) -> CampaignSchema:
    """Get a campaign by SQID."""
    campaign = await get_or_404(transaction, Campaign, id)
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
