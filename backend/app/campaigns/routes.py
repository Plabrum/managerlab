from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaigns.models import Campaign
from app.base.schemas import SanitizedSQLAlchemyDTO, UpdateSQLAlchemyDTO
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_authenticated_user

# Register CampaignObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.campaigns.objects import CampaignObject

ObjectRegistry().register(ObjectTypes.Campaigns, CampaignObject)


class CampaignDTO(SanitizedSQLAlchemyDTO[Campaign]):
    """Data transfer object for Campaign model."""

    pass


class CampaignUpdateDTO(UpdateSQLAlchemyDTO[Campaign]):
    """DTO for partial Campaign updates."""

    pass


@get("/{id:str}", return_dto=CampaignDTO)
async def get_campaign(id: Sqid, transaction: AsyncSession) -> Campaign:
    """Get a campaign by SQID."""
    campaign_id = sqid_decode(id)
    campaign = await transaction.get(Campaign, campaign_id)
    if not campaign:
        raise ValueError(f"Campaign with id {id} not found")
    return campaign


@post("/{id:str}", return_dto=CampaignDTO)
async def update_campaign(
    id: Sqid, data: CampaignUpdateDTO, transaction: AsyncSession
) -> Campaign:
    """Update a campaign by SQID."""
    campaign_id = sqid_decode(id)
    campaign = await transaction.get(Campaign, campaign_id)
    if not campaign:
        raise ValueError(f"Campaign with id {id} not found")

    # Apply updates from DTO - partial=True means only provided fields are included
    for field, value in data.__dict__.items():
        if hasattr(campaign, field):  # Only update existing model fields
            setattr(campaign, field, value)

    await transaction.flush()
    return campaign


# Campaign router
campaign_router = Router(
    path="/campaigns",
    guards=[requires_authenticated_user],
    route_handlers=[
        get_campaign,
        update_campaign,
    ],
    tags=["campaigns"],
)
