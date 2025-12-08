from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.actions.base import (
    BaseObjectAction,
    BaseTopLevelAction,
    EmptyActionData,
    action_group_factory,
)
from app.actions.deps import ActionDeps
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.actions.state_actions import BaseUpdateStateAction, UpdateStateData
from app.deliverables.enums import DeliverableActions, DeliverableStates
from app.deliverables.models import Deliverable, DeliverableMedia
from app.deliverables.schemas import (
    AddMediaToDeliverableSchema,
    DeliverableCreateSchema,
    DeliverableUpdateSchema,
)
from app.media.models import Media
from app.utils.db import create_model, update_model

deliverable_actions = action_group_factory(ActionGroupType.DeliverableActions, model_type=Deliverable)


@deliverable_actions
class DeleteDeliverable(BaseObjectAction[Deliverable, EmptyActionData]):
    action_key = DeliverableActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 100
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this deliverable?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls, obj: Deliverable, data: EmptyActionData, transaction: AsyncSession, deps
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted deliverable",
        )


@deliverable_actions
class EditDeliverable(BaseObjectAction[Deliverable, DeliverableUpdateSchema]):
    action_key = DeliverableActions.update
    label = "Edit"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Deliverable,
        data: DeliverableUpdateSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=deps.user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated deliverable",
        )


@deliverable_actions
class PublishDeliverable(BaseObjectAction[Deliverable, EmptyActionData]):
    """Publish a draft deliverable."""

    action_key = DeliverableActions.publish
    label = "Publish"
    is_bulk_allowed = True
    priority = 1
    icon = ActionIcon.send

    @classmethod
    async def execute(
        cls, obj: Deliverable, data: EmptyActionData, transaction: AsyncSession, deps
    ) -> ActionExecutionResponse:
        obj.state = DeliverableStates.POSTED

        return ActionExecutionResponse(
            message="Published deliverable",
        )

    @classmethod
    def is_available(cls, obj: Deliverable | None, deps) -> bool:
        return obj is not None and obj.state == DeliverableStates.DRAFT


@deliverable_actions
class AddMediaToDeliverable(BaseObjectAction[Deliverable, AddMediaToDeliverableSchema]):
    """Add media files to a deliverable."""

    action_key = DeliverableActions.add_media
    label = "Add Media"
    is_bulk_allowed = False
    priority = 0
    icon = ActionIcon.add
    model = Deliverable
    load_options = [selectinload(Deliverable.media)]

    @classmethod
    async def execute(
        cls,
        obj: Deliverable,
        data: AddMediaToDeliverableSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # media_ids are already decoded from SQID strings to ints by msgspec
        requested_media_ids = data.media_ids
        result = await transaction.execute(select(Media).where(Media.id.in_(requested_media_ids)))
        media_objects = result.scalars().all()

        # Check if all requested media were found
        if len(media_objects) != len(data.media_ids):
            found_ids = {media.id for media in media_objects}
            # Convert to int for set operations
            missing_ids = set(int(mid) for mid in requested_media_ids) - found_ids
            return ActionExecutionResponse(
                message=f"Media not found: {missing_ids}",
            )

        # Add media to deliverable via association table (only add if not already associated)
        # Use set-based comparison to avoid N+1 queries
        existing_media_ids = {media.id for media in obj.media}
        new_media_ids = [media.id for media in media_objects if media.id not in existing_media_ids]

        # Create DeliverableMedia association objects for new media
        for media_id in new_media_ids:
            association = DeliverableMedia(
                team_id=deps.team_id,
                deliverable_id=obj.id,
                media_id=media_id,
                approved_at=None,
                is_featured=False,
            )
            transaction.add(association)

        return ActionExecutionResponse(
            message=f"Added {len(new_media_ids)} media file(s) to deliverable",
        )


@deliverable_actions
class CreateDeliverable(BaseTopLevelAction[DeliverableCreateSchema]):
    action_key = DeliverableActions.create
    label = "Create Deliverable"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: DeliverableCreateSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        deliverable = await create_model(
            session=transaction,
            team_id=deps.team_id,
            campaign_id=None,
            model_class=Deliverable,
            create_vals=data,
            user_id=deps.user,
        )
        return ActionExecutionResponse(
            message=f"Created deliverable '{deliverable.title}'",
        )


@deliverable_actions
class UpdateDeliverableState(BaseUpdateStateAction[Deliverable, DeliverableStates]):
    action_key = DeliverableActions.update_state
    state_enum = DeliverableStates
