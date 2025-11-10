from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseObjectAction, action_group_factory
from app.actions.base import EmptyActionData
from app.actions.deps import ActionDeps
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.dashboard.enums import DashboardActions
from app.dashboard.models import Dashboard
from app.dashboard.schemas import UpdateDashboardSchema
from app.utils.db import update_model

dashboard_actions = action_group_factory(
    ActionGroupType.DashboardActions,
    model_type=Dashboard,
)


@dashboard_actions
class DeleteDashboard(BaseObjectAction[Dashboard, EmptyActionData]):
    """Delete a dashboard."""

    action_key = DashboardActions.delete
    label = "Delete"
    is_bulk_allowed = False
    priority = 100
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this dashboard?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls, obj: Dashboard, data: EmptyActionData, transaction: AsyncSession, deps
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Dashboard deleted successfully",
        )


@dashboard_actions
class UpdateDashboard(BaseObjectAction[Dashboard, UpdateDashboardSchema]):
    """Update a dashboard."""

    action_key = DashboardActions.update
    label = "Update"
    is_bulk_allowed = False
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Dashboard,
        data: UpdateDashboardSchema,
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
            message="Dashboard updated successfully",
        )
