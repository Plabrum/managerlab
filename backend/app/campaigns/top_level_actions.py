from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction, action_group_factory, ActionGroupType
from app.actions.enums import ActionIcon
from app.campaigns.models import Campaign
from app.campaigns.enums import CampaignActions
from app.campaigns.schemas import CampaignCreateSchema
from app.campaigns.objects import CampaignObject
from app.utils.db import create_model


top_level_campaign_actions = action_group_factory(
    ActionGroupType.TopLevelCampaignActions,
    model_type=Campaign,
    object_service=CampaignObject,
)


@top_level_campaign_actions
class CreateCampaign(BaseAction):
    action_key = CampaignActions.create
    label = "Create Campaign"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: CampaignCreateSchema,
        transaction: AsyncSession,
        team_id: int,
        user: int,
    ) -> Campaign:
        # brand_id is already decoded from SQID string to int by msgspec
        new_campaign = await create_model(
            session=transaction,
            team_id=team_id,
            campaign_id=None,
            model_class=Campaign,
            create_vals=data,
            user_id=user,
        )
        return new_campaign
