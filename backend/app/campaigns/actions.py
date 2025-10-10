from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import action_group_factory, ActionGroupType, BaseAction
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.campaigns.enums import CampaignActions
from app.campaigns.models import Campaign
from app.campaigns.routes import CampaignUpdateDTO
from app.utils.dto import update_model


campaign_actions = action_group_factory(
    ActionGroupType.CampaignActions,
    model_type=Campaign,
)


@campaign_actions
class DeleteCampaign(BaseAction):
    action_key = CampaignActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this campaign?"

    @classmethod
    async def execute(
        cls,
        obj: Campaign,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            success=True,
            message="Deleted campaign",
            results={},
        )


@campaign_actions
class UpdateCampaign(BaseAction):
    action_key = CampaignActions.update
    label = "Update"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Campaign,
        data: CampaignUpdateDTO,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        update_model(obj, data)
        transaction.add(obj)

        return ActionExecutionResponse(
            success=True,
            message="Updated campaign",
            results={},
        )
