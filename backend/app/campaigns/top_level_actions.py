from litestar.dto import DTOData
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction, action_group_factory, ActionGroupType
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.campaigns.models import Campaign
from app.campaigns.enums import CampaignActions


top_level_campaign_actions = action_group_factory(
    ActionGroupType.TopLevelCampaignActions
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
        cls, data: DTOData[Campaign], transaction: AsyncSession
    ) -> ActionExecutionResponse:
        new_campaign = data.create_instance()
        transaction.add(new_campaign)
        return ActionExecutionResponse(
            success=True,
            message=f"Created campaign '{new_campaign.name}'",
            results={"campaign_id": new_campaign.id},
        )
