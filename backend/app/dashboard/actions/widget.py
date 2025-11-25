"""Widget actions for CRUD operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
from app.dashboard.enums import WidgetActions
from app.dashboard.models import Dashboard, Widget
from app.dashboard.schemas import (
    CreateWidgetSchema,
    EditWidgetSchema,
    ReorderWidgetsSchema,
)
from app.utils.db import update_model

widget_actions = action_group_factory(
    ActionGroupType.WidgetActions,
    model_type=Widget,
    load_options=[selectinload(Widget.dashboard)],
)


@widget_actions
class CreateWidget(BaseTopLevelAction[CreateWidgetSchema]):
    """Create a new widget."""

    action_key = WidgetActions.create
    label = "Add Widget"
    priority = 10
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: CreateWidgetSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # Verify dashboard exists and user has access
        dashboard = await transaction.get(Dashboard, data.dashboard_id)
        if not dashboard:
            raise ValueError("Dashboard not found")

        # Get default size for widget type
        from app.dashboard.enums import get_widget_size_constraints

        constraints = get_widget_size_constraints(data.type)

        widget = Widget(
            dashboard_id=data.dashboard_id,
            team_id=deps.team_id,
            type=data.type,
            title=data.title,
            description=data.description,
            query=data.query,
            position_x=data.position_x,
            position_y=data.position_y,
            size_w=data.size_w or constraints["default_w"],
            size_h=data.size_h or constraints["default_h"],
        )
        transaction.add(widget)
        await transaction.flush()

        return ActionExecutionResponse(
            message="Widget created successfully",
            invalidate_queries=["dashboards", "widgets"],
        )


@widget_actions
class EditWidget(BaseObjectAction[Widget, EditWidgetSchema]):
    """Update a widget."""

    action_key = WidgetActions.edit
    label = "Edit Widget Query"
    priority = 10
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Widget,
        data: EditWidgetSchema,
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
            message="Widget updated successfully",
            invalidate_queries=["dashboards", "widgets"],
        )


@widget_actions
class DeleteWidget(BaseObjectAction[Widget, EmptyActionData]):
    """Delete a widget."""

    action_key = WidgetActions.delete
    label = "Delete"
    priority = 100
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this widget?"

    @classmethod
    async def execute(
        cls,
        obj: Widget,
        data: EmptyActionData,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)

        return ActionExecutionResponse(
            message="Widget deleted successfully",
            invalidate_queries=["dashboards", "widgets"],
        )


@widget_actions
class ReorderWidgets(BaseTopLevelAction[ReorderWidgetsSchema]):
    """Reorder widgets (batch position update)."""

    action_key = WidgetActions.reorder
    label = "Reorder Widgets"
    priority = 20
    icon = ActionIcon.edit
    # This action is typically called programmatically, not shown in UI
    hidden = True

    @classmethod
    async def execute(
        cls,
        data: ReorderWidgetsSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # Verify dashboard exists and user has access
        dashboard = await transaction.get(Dashboard, data.dashboard_id)
        if not dashboard:
            raise ValueError("Dashboard not found")

        # Update each widget's position and size
        for widget_pos in data.widgets:
            widget = await transaction.get(Widget, widget_pos.id)
            if widget and widget.dashboard_id == data.dashboard_id:
                widget.position_x = widget_pos.position_x
                widget.position_y = widget_pos.position_y

                # Update size if provided
                if widget_pos.size_w is not None:
                    widget.size_w = max(1, min(6, widget_pos.size_w))  # Clamp 1-6
                if widget_pos.size_h is not None:
                    widget.size_h = max(1, widget_pos.size_h)  # Clamp ≥1

        return ActionExecutionResponse(
            message="Widgets reordered successfully",
            invalidate_queries=["dashboards", "widgets"],
        )
