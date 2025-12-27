import msgspec
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.views.enums import SavedViewActions
from app.views.models import SavedView
from app.views.schemas import CreateSavedViewSchema, UpdateSavedViewSchema

saved_view_actions = action_group_factory(
    ActionGroupType.SavedViewActions,
    model_type=SavedView,
)


@saved_view_actions
class CreateSavedView(BaseTopLevelAction[CreateSavedViewSchema]):
    """Create a new saved view."""

    action_key = SavedViewActions.create
    label = "Save as View"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: CreateSavedViewSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # Create saved view with user_id set if it's a personal view
        new_view = SavedView(
            name=data.name,
            object_type=data.object_type,
            config=msgspec.structs.asdict(data.config),  # Convert Struct to dict
            user_id=deps.user if data.is_personal else None,
            team_id=deps.team_id,
        )
        transaction.add(new_view)
        await transaction.flush()

        return ActionExecutionResponse(
            message=f"Created view '{new_view.name}'",
            created_id=new_view.id,
            invalidate_queries=["views"],
        )


@saved_view_actions
class UpdateSavedView(BaseObjectAction[SavedView, UpdateSavedViewSchema]):
    """Update a saved view's name or configuration."""

    action_key = SavedViewActions.update
    label = "Update View"
    is_bulk_allowed = False
    priority = 10
    icon = ActionIcon.edit

    @classmethod
    async def can_execute(cls, obj: SavedView, deps: ActionDeps) -> tuple[bool, str | None]:
        """Check if user can update this view.

        Only personal view owners can update their views.
        Team-shared views cannot be updated.
        """
        if obj.is_team_shared:
            return False, "Team-shared views cannot be updated"

        if obj.is_personal and obj.user_id != deps.user:
            return False, "You can only update your own views"

        return True, None

    @classmethod
    async def execute(
        cls,
        obj: SavedView,
        data: UpdateSavedViewSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # Update fields directly on the model
        if data.name is not None:
            obj.name = data.name
        if data.config is not None:
            obj.config = msgspec.structs.asdict(data.config)

        await transaction.flush()

        return ActionExecutionResponse(
            message=f"Updated view '{obj.name}'",
            invalidate_queries=["views"],
        )


@saved_view_actions
class DeleteSavedView(BaseObjectAction[SavedView, EmptyActionData]):
    """Delete a saved view."""

    action_key = SavedViewActions.delete
    label = "Delete View"
    is_bulk_allowed = False
    priority = 100
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this view?"

    @classmethod
    async def can_execute(cls, obj: SavedView, deps: ActionDeps) -> tuple[bool, str | None]:
        """Check if user can delete this view.

        Only personal view owners can delete their views.
        Team-shared views cannot be deleted.
        """
        if obj.is_team_shared:
            return False, "Team-shared views cannot be deleted"

        if obj.is_personal and obj.user_id != deps.user:
            return False, "You can only delete your own views"

        return True, None

    @classmethod
    async def execute(
        cls,
        obj: SavedView,
        data: EmptyActionData,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message=f"Deleted view '{obj.name}'",
            invalidate_queries=["views"],
        )


@saved_view_actions
class DuplicateSavedView(BaseObjectAction[SavedView, EmptyActionData]):
    """Duplicate a saved view."""

    action_key = SavedViewActions.duplicate
    label = "Duplicate View"
    is_bulk_allowed = False
    priority = 20
    icon = ActionIcon.default

    @classmethod
    async def execute(
        cls,
        obj: SavedView,
        data: EmptyActionData,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # Create a copy of the view as a personal view for the current user
        new_view = SavedView(
            name=f"{obj.name} (Copy)",
            object_type=obj.object_type,
            config=obj.config.copy(),  # Copy the config dict
            user_id=deps.user,  # Always create as personal view
            team_id=deps.team_id,
        )
        transaction.add(new_view)
        await transaction.flush()

        return ActionExecutionResponse(
            message=f"Duplicated view as '{new_view.name}'",
            created_id=new_view.id,
            invalidate_queries=["views"],
        )
