from datetime import UTC

from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import (
    ActionGroupType,
    BaseObjectAction,
    BaseTopLevelAction,
    action_group_factory,
)
from app.actions.base import EmptyActionData
from app.actions.deps import ActionDeps
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.addresses.models import Address
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
        from datetime import datetime

        # Soft delete by setting deleted_at
        obj.deleted_at = datetime.now(tz=UTC)
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
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # Handle creation of new address (update_model can't auto-create)
        if data.address and not obj.address:
            obj.address = Address(
                team_id=obj.team_id,
                address1=data.address.address1,
                address2=data.address.address2,
                city=data.address.city,
                state=data.address.state,
                zip=data.address.zip,
                country=data.address.country,
                address_type=data.address.address_type,
            )

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
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        roster = Roster(
            user_id=deps.user,
            team_id=deps.team_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            birthdate=data.birthdate,
            gender=data.gender,
            instagram_handle=data.instagram_handle,
            facebook_handle=data.facebook_handle,
            tiktok_handle=data.tiktok_handle,
            youtube_channel=data.youtube_channel,
            profile_photo_id=data.profile_photo_id,
        )

        if data.address:
            roster.address = Address(
                team_id=deps.team_id,
                address1=data.address.address1,
                address2=data.address.address2,
                city=data.address.city,
                state=data.address.state,
                zip=data.address.zip,
                country=data.address.country,
                address_type=data.address.address_type,
            )

        transaction.add(roster)
        await transaction.flush()
        return ActionExecutionResponse(
            message="Created roster member",
            created_id=roster.id,
        )
