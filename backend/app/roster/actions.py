from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import action_group_factory, ActionGroupType, BaseAction
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.roster.models import Roster
from app.roster.enums import RosterActions
from app.roster.schemas import RosterUpdateSchema
from app.utils.db import update_model


# Create roster action group
roster_actions = action_group_factory(
    ActionGroupType.RosterActions,
    model_type=Roster,
)


@roster_actions
class DeleteRoster(BaseAction):
    action_key = RosterActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this roster member?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls,
        obj: Roster,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            success=True,
            message="Deleted roster member",
            results={},
            should_redirect_to_parent=True,
        )


@roster_actions
class UpdateRoster(BaseAction):
    action_key = RosterActions.update
    label = "Edit"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Roster,
        data: RosterUpdateSchema,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        update_model(obj, data)

        return ActionExecutionResponse(
            success=True,
            message="Updated roster member",
            results={},
        )
