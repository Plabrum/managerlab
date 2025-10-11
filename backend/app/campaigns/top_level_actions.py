from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction, action_group_factory, ActionGroupType
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.campaigns.models import Campaign
from app.campaigns.enums import CampaignActions
from app.campaigns.routes import CampaignCreateDTO
from app.utils.dto import create_model


top_level_campaign_actions = action_group_factory(
    ActionGroupType.TopLevelCampaignActions,
    model_type=Campaign,
)


@top_level_campaign_actions
class CreateCampaign(BaseAction):
    action_key = CampaignActions.create
    label = "Create Campaign"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(  # type: ignore[override]
        cls, data: CampaignCreateDTO, transaction: AsyncSession
    ) -> ActionExecutionResponse:
        new_campaign = create_model(Campaign, data)
        transaction.add(new_campaign)
        return ActionExecutionResponse(
            success=True,
            message=f"Created campaign '{new_campaign.name}'",
            results={"campaign_id": new_campaign.id},
        )
