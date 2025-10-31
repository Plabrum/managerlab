from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseAction, action_group_factory
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.campaigns.enums import CampaignActions
from app.campaigns.models import Campaign
from app.campaigns.schemas import CampaignUpdateSchema
from app.utils.db import update_model

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
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls,
        obj: Campaign,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted campaign",
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
        data: CampaignUpdateSchema,
        transaction: AsyncSession,
        user: int,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated campaign",
        )
