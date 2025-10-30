from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.actions.base import BaseAction, action_group_factory
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.deliverables.enums import DeliverableMediaActions
from app.deliverables.models import DeliverableMedia

deliverable_media_actions = action_group_factory(
    ActionGroupType.DeliverableMediaActions,
    model_type=DeliverableMedia,
)


@deliverable_media_actions
class RemoveMediaFromDeliverable(BaseAction):
    """Remove media files from a deliverable."""

    action_key = DeliverableMediaActions.remove_media
    label = "Remove Media"
    is_bulk_allowed = False
    priority = 11
    icon = ActionIcon.trash
    load_options = [
        joinedload(DeliverableMedia.deliverable),
        joinedload(DeliverableMedia.thread),
    ]

    @classmethod
    async def execute(
        cls,
        obj: DeliverableMedia,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        # Delete the DeliverableMedia association object
        await transaction.delete(obj)

        return ActionExecutionResponse(
            message="Removed media from deliverable",
        )


@deliverable_media_actions
class AcceptDeliverableMedia(BaseAction):
    """Accept/approve a media file in a deliverable."""

    action_key = DeliverableMediaActions.accept
    label = "Accept"
    is_bulk_allowed = True
    priority = 1
    icon = ActionIcon.check
    load_options = [
        joinedload(DeliverableMedia.deliverable),
        joinedload(DeliverableMedia.thread),
    ]

    @classmethod
    async def execute(
        cls,
        obj: DeliverableMedia,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        # Set approved_at to current time
        obj.approved_at = datetime.now(tz=UTC)

        return ActionExecutionResponse(
            message="Accepted media",
        )

    @classmethod
    def is_available(cls, obj: DeliverableMedia | None) -> bool:
        # Only available if not already approved
        return obj is not None and obj.approved_at is None


@deliverable_media_actions
class RejectDeliverableMedia(BaseAction):
    """Reject/unapprove a media file in a deliverable."""

    action_key = DeliverableMediaActions.reject
    label = "Reject"
    is_bulk_allowed = True
    priority = 2
    icon = ActionIcon.x
    load_options = [
        joinedload(DeliverableMedia.deliverable),
        joinedload(DeliverableMedia.thread),
    ]

    @classmethod
    async def execute(
        cls,
        obj: DeliverableMedia,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        # Set approved_at to None
        obj.approved_at = None

        return ActionExecutionResponse(
            message="Rejected media",
        )

    @classmethod
    def is_available(cls, obj: DeliverableMedia | None) -> bool:
        # Only available if already approved
        return obj is not None and obj.approved_at is not None
