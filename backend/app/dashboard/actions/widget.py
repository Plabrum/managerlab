"""Widget actions for CRUD operations."""

import msgspec
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified

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
)
from app.utils.db import get_or_404

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
        # Verify dashboard exists and load for update
        dashboard = await get_or_404(transaction, Dashboard, data.dashboard_id)

        # Convert WidgetQuerySchema to dict for JSONB storage
        query_dict = msgspec.structs.asdict(data.query)

        # Create widget WITHOUT position columns
        widget = Widget(
            dashboard_id=data.dashboard_id,
            team_id=deps.team_id,
            type=data.type,
            title=data.title,
            description=data.description,
            query=query_dict,
        )
        transaction.add(widget)
        await transaction.flush()  # Get widget.id

        # Add to dashboard layout
        if "layout" not in dashboard.config:
            dashboard.config["layout"] = []

        dashboard.config["layout"].append(
            {
                "i": str(widget.id),
                "x": data.position_x,
                "y": data.position_y,
                "w": data.size_w,
                "h": data.size_h,
            }
        )

        # Mark config as modified so SQLAlchemy tracks the change
        flag_modified(dashboard, "config")

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
        # Convert WidgetQuerySchema to dict if query is being updated
        if data.query is not None:
            import msgspec

            query_dict = msgspec.structs.asdict(data.query)
            # Directly update the widget with the dict query
            obj.query = query_dict

        # Update other fields using update_model, but exclude query
        # Build update dict with only non-None values (excluding query)
        update_dict = {}
        if data.type is not None:
            update_dict["type"] = data.type
        if data.title is not None:
            update_dict["title"] = data.title
        if data.description is not None:
            update_dict["description"] = data.description

        # Apply updates to the object
        for key, value in update_dict.items():
            setattr(obj, key, value)

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
    load_options = [joinedload(Widget.dashboard)]

    @classmethod
    async def execute(
        cls,
        obj: Widget,
        data: EmptyActionData,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        widget_id = str(obj.id)
        dashboard = obj.dashboard

        # Remove from dashboard layout
        if "layout" in dashboard.config:
            dashboard.config["layout"] = [item for item in dashboard.config["layout"] if item["i"] != widget_id]
            # Mark config as modified so SQLAlchemy tracks the change
            flag_modified(dashboard, "config")

        await transaction.delete(obj)

        return ActionExecutionResponse(
            message="Widget deleted successfully",
            invalidate_queries=["dashboards", "widgets"],
        )
