from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction, action_group_factory
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.base.models import BaseDBModel
from app.deliverables.models import Deliverable
from app.deliverables.enums import TopLevelDeliverableActions
from app.deliverables.schemas import DeliverableCreateSchema
from app.utils.db import create_model


top_level_deliverable_actions = action_group_factory(
    ActionGroupType.TopLevelDeliverableActions
)


class DeliverableTopLevelActionMixin:
    """Mixin for deliverable top-level actions."""

    @classmethod
    def get_model(cls) -> Type[BaseDBModel] | None:
        """Top-level actions don't operate on specific instances."""
        return None


@top_level_deliverable_actions
class CreateDeliverable(DeliverableTopLevelActionMixin, BaseAction):
    action_key = TopLevelDeliverableActions.create
    label = "Create Deliverable"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        obj: Deliverable,
        data: DeliverableCreateSchema,
        transaction: AsyncSession,
        team_id: int,
    ) -> ActionExecutionResponse:
        deliverable = create_model(
            team_id=team_id,
            campaign_id=None,
            model_class=Deliverable,
            create_vals=data,
        )
        transaction.add(deliverable)
        return ActionExecutionResponse(
            success=True,
            message="Created deliverable ",
            results={"deliverable_id": deliverable.id},
        )
