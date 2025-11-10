from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseObjectAction, BaseTopLevelAction, action_group_factory
from app.actions.base import EmptyActionData
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.roster.enums import RosterActions
from app.roster.models import Roster
from app.roster.schemas import RosterCreateSchema, RosterUpdateSchema
from app.utils.db import update_model

# Create roster action group
roster_actions = action_group_factory(
    ActionGroupType.RosterActions,
    model_type=Roster,
)


@roster_actions
class DeleteRoster(BaseObjectAction[Roster, EmptyActionData]):
    action_key = RosterActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this roster member?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls, obj: Roster, data: EmptyActionData, transaction: AsyncSession, deps
    ) -> ActionExecutionResponse:
        from datetime import datetime, timezone

        # Soft delete by setting deleted_at
        obj.deleted_at = datetime.now(tz=timezone.utc)
        await transaction.flush()
        return ActionExecutionResponse(
            message="Deleted roster member",
        )


@roster_actions
class UpdateRoster(BaseObjectAction[Roster, RosterUpdateSchema]):
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
        deps,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=deps.user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated roster member",
        )


@roster_actions
class CreateRoster(BaseTopLevelAction[RosterCreateSchema]):
    action_key = RosterActions.create
    label = "Create Roster Member"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: RosterCreateSchema,
        transaction: AsyncSession,
        deps,
    ) -> ActionExecutionResponse:
        # Get user_id from session
        user_id = deps.request.session.get("user_id")
        if not user_id:
            return ActionExecutionResponse(
                message="User not authenticated",
            )

        # Create roster member
        roster = Roster(
            user_id=user_id,
            team_id=deps.team_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            instagram_handle=data.instagram_handle,
        )
        transaction.add(roster)
        return ActionExecutionResponse(
            message="Created roster member",
        )
