from datetime import UTC

from msgspec import UNSET, structs
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
        # Handle address update separately (nested object)
        update_dict = structs.asdict(data)
        address_data = update_dict.pop("address", UNSET)

        if address_data is not UNSET:
            if address_data is None:
                # Clear address reference
                obj.address_id = None
            else:
                # Create or update address
                if obj.address_id:
                    # Update existing address
                    await update_model(
                        session=transaction,
                        model_instance=obj.address,
                        update_vals=address_data,
                        user_id=deps.user,
                        team_id=obj.team_id,
                    )
                else:
                    # Create new address
                    address = Address(
                        team_id=deps.team_id,
                        address1=address_data.address1,
                        address2=address_data.address2,
                        city=address_data.city,
                        state=address_data.state,
                        zip=address_data.zip,
                        country=address_data.country,
                        address_type=address_data.address_type,
                    )
                    transaction.add(address)
                    await transaction.flush()
                    obj.address_id = address.id

        # Update remaining fields (excluding address)
        remaining_fields = {k: v for k, v in update_dict.items() if v is not UNSET}
        if remaining_fields:
            # Create a new schema with only the fields that were set
            from msgspec import Struct

            # Dynamically create struct with remaining fields
            for field, value in remaining_fields.items():
                if hasattr(obj, field):
                    setattr(obj, field, value)

        # Flush changes to database
        await transaction.flush()

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
        # Get user_id from session
        user_id = deps.request.session.get("user_id")
        if not user_id:
            return ActionExecutionResponse(
                message="User not authenticated",
            )

        # Create address first if provided
        address_id = None
        if data.address:
            address = Address(
                team_id=deps.team_id,
                address1=data.address.address1,
                address2=data.address.address2,
                city=data.address.city,
                state=data.address.state,
                zip=data.address.zip,
                country=data.address.country,
                address_type=data.address.address_type,
            )
            transaction.add(address)
            await transaction.flush()  # Get address ID
            address_id = address.id

        # Create roster member with address reference
        roster = Roster(
            user_id=user_id,
            team_id=deps.team_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            birthdate=data.birthdate,
            gender=data.gender,
            address_id=address_id,
            instagram_handle=data.instagram_handle,
            facebook_handle=data.facebook_handle,
            tiktok_handle=data.tiktok_handle,
            youtube_channel=data.youtube_channel,
        )
        transaction.add(roster)
        await transaction.flush()
        return ActionExecutionResponse(
            message="Created roster member",
            created_id=roster.id,
        )
