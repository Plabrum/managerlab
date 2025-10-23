from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.actions.base import BaseAction, action_group_factory
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.deliverables.enums import DeliverableStates, DeliverableActions
from app.deliverables.models import Deliverable, DeliverableMedia
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
    priority = 100
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
class EditDeliverable(BaseAction):
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
    ) -> ActionExecutionResponse:
        update_model(obj, data)
        # No need to add(obj) - it's already tracked by the session that loaded it

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
    ) -> ActionExecutionResponse:
        # media_ids are already decoded from SQID strings to ints by msgspec
        requested_media_ids = data.media_ids
        result = await transaction.execute(
            select(Media).where(Media.id.in_(requested_media_ids))
        )
        media_objects = result.scalars().all()

        # Check if all requested media were found
        if len(media_objects) != len(data.media_ids):
            found_ids = {media.id for media in media_objects}
            # Convert to int for set operations
            missing_ids = set(int(mid) for mid in requested_media_ids) - found_ids
            return ActionExecutionResponse(
                success=False,
                message=f"Media not found: {missing_ids}",
                results={},
            )

        # Add media to deliverable via association table (only add if not already associated)
        # Use set-based comparison to avoid N+1 queries
        existing_media_ids = {media.id for media in obj.media}
        new_media_ids = [
            media.id for media in media_objects if media.id not in existing_media_ids
        ]

        # Create DeliverableMedia association objects for new media
        for media_id in new_media_ids:
            association = DeliverableMedia(
                deliverable_id=obj.id,
                media_id=media_id,
                approved_at=None,
                is_featured=False,
            )
            transaction.add(association)

        return ActionExecutionResponse(
            success=True,
            message=f"Added {len(new_media_ids)} media file(s) to deliverable",
            results={"added_count": len(new_media_ids)},
        )


@deliverable_actions
class RemoveMediaFromDeliverable(BaseAction):
    """Remove media files from a deliverable."""

    action_key = DeliverableActions.remove_media
    label = "Remove Media"
    is_bulk_allowed = False
    priority = 11
    icon = ActionIcon.trash
    model = Deliverable
    load_options = [selectinload(Deliverable.media)]

    @classmethod
    async def execute(
        cls,
        obj: Deliverable,
        data: RemoveMediaFromDeliverableSchema,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        # media_ids are already decoded from SQID strings to ints by msgspec
        requested_media_ids = data.media_ids

        # Remove media from deliverable using set-based comparison
        existing_media_ids = {media.id for media in obj.media}
        media_ids_to_remove = set(requested_media_ids) & existing_media_ids

        # Delete DeliverableMedia association objects
        result = await transaction.execute(
            select(DeliverableMedia).where(
                DeliverableMedia.deliverable_id == obj.id,
                DeliverableMedia.media_id.in_(media_ids_to_remove),
            )
        )
        associations = result.scalars().all()

        for association in associations:
            await transaction.delete(association)

        removed_count = len(associations)

        return ActionExecutionResponse(
            success=True,
            message=f"Removed {removed_count} media file(s) from deliverable",
            results={"removed_count": removed_count},
        )
