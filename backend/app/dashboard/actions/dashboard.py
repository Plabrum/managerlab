from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.actions import ActionGroupType, BaseObjectAction, BaseTopLevelAction, action_group_factory
from app.actions.base import EmptyActionData
from app.actions.deps import ActionDeps
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.dashboard.enums import DashboardActions
from app.dashboard.models import Dashboard
from app.dashboard.schemas import CreateDashboardSchema, UpdateDashboardSchema
from app.utils.db import update_model

dashboard_actions = action_group_factory(
    ActionGroupType.DashboardActions,
    model_type=Dashboard,
    load_options=[selectinload(Dashboard.widgets)],
)


@dashboard_actions
class CreateDashboard(BaseTopLevelAction[CreateDashboardSchema]):
    """Create a new dashboard."""

    action_key = DashboardActions.create
    label = "Create Dashboard"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: CreateDashboardSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # Create dashboard with user_id set if it's a personal dashboard
        new_dashboard = Dashboard(
            name=data.name,
            config=data.config,
            user_id=deps.user if data.is_personal else None,
            team_id=deps.team_id,
            is_default=data.is_default,
        )
        transaction.add(new_dashboard)
        await transaction.flush()

        return ActionExecutionResponse(
            message=f"Created dashboard '{new_dashboard.name}'",
            created_id=new_dashboard.id,
            invalidate_queries=["dashboards"],
        )


@dashboard_actions
class EditDashboard(BaseObjectAction[Dashboard, EmptyActionData]):
    """Edit dashboard layout and widgets."""

    action_key = DashboardActions.edit
    label = "Customize"
    is_bulk_allowed = False
    priority = 10  # Higher priority than update/delete so it appears first
    icon = ActionIcon.edit
    # No confirmation needed - just enables edit mode on frontend
    # No form needed - this is a frontend-only mode toggle

    @classmethod
    async def execute(
        cls, obj: Dashboard, data: EmptyActionData, transaction: AsyncSession, deps
    ) -> ActionExecutionResponse:
        # This action doesn't actually modify the backend
        # It's used to check permissions and enable edit mode on the frontend
        return ActionExecutionResponse(
            message="Edit mode enabled",
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
    label = "Rename"
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
