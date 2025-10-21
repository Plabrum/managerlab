from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.base import BaseAction, action_group_factory
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.deliverables.enums import DeliverableStates, DeliverableActions
from app.deliverables.models import Deliverable
from app.deliverables.schemas import DeliverableUpdateSchema
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
