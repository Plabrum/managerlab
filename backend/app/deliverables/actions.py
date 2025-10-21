from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.base import BaseAction, action_group_factory
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.deliverables.enums import DeliverableStates, DeliverableActions
from app.deliverables.models import Deliverable
from app.deliverables.schemas import (
    AddMediaToDeliverableSchema,
    DeliverableUpdateSchema,
    RemoveMediaFromDeliverableSchema,
)
from app.media.models import Media
from app.utils.db import update_model

deliverable_actions = action_group_factory(
    ActionGroupType.DeliverableActions, model_type=Deliverable
)


@deliverable_actions
class DeleteDeliverable(BaseAction):
    action_key = DeliverableActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this deliverable?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls,
        obj: Deliverable,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            success=True,
            message="Deleted deliverable",
            results={},
            should_redirect_to_parent=True,
        )


@deliverable_actions
class UpdateDeliverable(BaseAction):
    action_key = DeliverableActions.update
    label = "Update"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Deliverable,
        data: DeliverableUpdateSchema,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        update_model(obj, data)
        transaction.add(obj)

        return ActionExecutionResponse(
            success=True,
            message="Updated deliverable",
            results={},
        )


@deliverable_actions
class PublishDeliverable(BaseAction):
    """Publish a draft deliverable."""

    action_key = DeliverableActions.publish
    label = "Publish"
    is_bulk_allowed = True
    priority = 1
    icon = ActionIcon.send

    @classmethod
    async def execute(
        cls,
        obj: Deliverable,
    ) -> ActionExecutionResponse:
        obj.state = DeliverableStates.POSTED

        return ActionExecutionResponse(
            success=True,
            message="Published deliverable",
            results={},
        )

    @classmethod
    def is_available(cls, obj: Deliverable | None) -> bool:
        return obj is not None and obj.state == DeliverableStates.DRAFT


@deliverable_actions
class AddMediaToDeliverable(BaseAction):
    """Add media files to a deliverable."""

    action_key = DeliverableActions.add_media
    label = "Add Media"
    is_bulk_allowed = False
    priority = 10
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        obj: Deliverable,
        data: AddMediaToDeliverableSchema,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        # Fetch media objects by IDs
        result = await transaction.execute(
            select(Media).where(Media.id.in_(data.media_ids))
        )
        media_objects = result.scalars().all()

        # Check if all requested media were found
        if len(media_objects) != len(data.media_ids):
            found_ids = {media.id for media in media_objects}
            missing_ids = set(data.media_ids) - found_ids
            return ActionExecutionResponse(
                success=False,
                message=f"Media not found: {missing_ids}",
                results={},
            )

        # Add media to deliverable (only add if not already associated)
        added_count = 0
        for media in media_objects:
            if media not in obj.media:
                obj.media.append(media)
                added_count += 1

        transaction.add(obj)

        return ActionExecutionResponse(
            success=True,
            message=f"Added {added_count} media file(s) to deliverable",
            results={"added_count": added_count, "total_media": len(obj.media)},
        )


@deliverable_actions
class RemoveMediaFromDeliverable(BaseAction):
    """Remove media files from a deliverable."""

    action_key = DeliverableActions.remove_media
    label = "Remove Media"
    is_bulk_allowed = False
    priority = 11
    icon = ActionIcon.trash

    @classmethod
    async def execute(
        cls,
        obj: Deliverable,
        data: RemoveMediaFromDeliverableSchema,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        # Fetch media objects by IDs
        result = await transaction.execute(
            select(Media).where(Media.id.in_(data.media_ids))
        )
        media_objects = result.scalars().all()

        # Remove media from deliverable
        removed_count = 0
        for media in media_objects:
            if media in obj.media:
                obj.media.remove(media)
                removed_count += 1

        transaction.add(obj)

        return ActionExecutionResponse(
            success=True,
            message=f"Removed {removed_count} media file(s) from deliverable",
            results={"removed_count": removed_count, "total_media": len(obj.media)},
        )
