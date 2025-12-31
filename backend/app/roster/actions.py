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
from app.utils.sqids import sqid_decode

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

        # Decode profile_photo_id from sqid to numeric ID if provided
        profile_photo_sqid = update_dict.pop("profile_photo_id", UNSET)
        if profile_photo_sqid is not UNSET:
            if profile_photo_sqid is None:
                update_dict["profile_photo_id"] = None
            else:
                update_dict["profile_photo_id"] = sqid_decode(str(profile_photo_sqid))

        if address_data is not UNSET:
            if address_data is None:
                # Clear address reference
                obj.address_id = None
            else:
                # Create or update address
                if obj.address_id and obj.address:
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
                        **address_data,  # Use dict unpacking for cleaner code
                    )
                    transaction.add(address)
                    await transaction.flush()
                    obj.address_id = address.id

        # Update remaining roster fields using standard update_model utility
        # This ensures proper event tracking and follows codebase conventions
        remaining_fields = {k: v for k, v in update_dict.items() if v is not UNSET}
        if remaining_fields:
            # Reconstruct RosterUpdateSchema with only the fields that were set
            # This allows update_model to properly track changes and emit events
            partial_update = RosterUpdateSchema(**remaining_fields)
            await update_model(
                session=transaction,
                model_instance=obj,
                update_vals=partial_update,
                user_id=deps.user,
                team_id=obj.team_id,
            )
        else:
            # If only address was updated, still need to flush the address_id change
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
            # Convert address schema to dict for cleaner instantiation
            address_dict = structs.asdict(data.address)
            address = Address(
                team_id=deps.team_id,
                **address_dict,  # Use dict unpacking
            )
            transaction.add(address)
            await transaction.flush()  # Get address ID
            address_id = address.id

        # Decode profile_photo_id from sqid to numeric ID if provided
        profile_photo_id = sqid_decode(str(data.profile_photo_id)) if data.profile_photo_id else None

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
            profile_photo_id=profile_photo_id,
        )
        transaction.add(roster)
        await transaction.flush()
        return ActionExecutionResponse(
            message="Created roster member",
            created_id=roster.id,
        )
