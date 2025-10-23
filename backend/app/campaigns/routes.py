from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaigns.models import Campaign
from app.campaigns.schemas import CampaignDTO, CampaignUpdateSchema
from app.utils.sqids import Sqid
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model

# Register CampaignObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.campaigns.objects import CampaignObject

ObjectRegistry().register(ObjectTypes.Campaigns, CampaignObject)


@get("/{id:str}", return_dto=CampaignDTO)
async def get_campaign(id: Sqid, transaction: AsyncSession) -> Campaign:
    """Get a campaign by SQID."""
    # id is already decoded from SQID string to int by msgspec
    return await get_or_404(transaction, Campaign, id)


@post("/{id:str}", return_dto=CampaignDTO)
async def update_campaign(
    id: Sqid, data: CampaignUpdateSchema, transaction: AsyncSession
) -> Campaign:
    """Update a campaign by SQID."""
    # id is already decoded from SQID string to int by msgspec
    campaign = await get_or_404(transaction, Campaign, id)
    update_model(campaign, data)
    await transaction.flush()
    return campaign


campaign_router = Router(
    path="/campaigns",
    guards=[requires_user_id],
    route_handlers=[
        get_campaign,
        update_campaign,
    ],
    tags=["campaigns"],
)
