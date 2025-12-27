"""Business logic for saved view operations."""

from datetime import UTC, datetime

import msgspec
from litestar.exceptions import PermissionDeniedException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.enums import ObjectTypes
from app.views.defaults import get_default_view_config
from app.views.models import SavedView
from app.views.schemas import SavedViewConfigSchema, SavedViewSchema


def check_view_ownership(view: SavedView, user_id: int) -> None:
    """Check if user has permission to modify a view.

    Raises PermissionDeniedException if user cannot modify the view.
    """
    if view.is_personal and view.user_id != user_id:
        raise PermissionDeniedException("You can only modify your own personal views")

    if view.is_team_shared:
        raise PermissionDeniedException("Team-shared views cannot be modified")


async def clear_user_defaults(
    session: AsyncSession,
    *,
    user_id: int,
    object_type: ObjectTypes,
) -> None:
    """Clear is_default flag on all user's views for the given object_type.

    Ensures only one view is marked as default per user per object_type.
    """
    stmt = (
        update(SavedView)
        .where(
            SavedView.user_id == user_id,
            SavedView.object_type == object_type,
            SavedView.is_default == True,  # noqa: E712
        )
        .values(is_default=False)
    )
    await session.execute(stmt)


def saved_view_to_schema(view: SavedView) -> SavedViewSchema:
    """Convert SavedView model to schema.

    Handles msgspec conversion of config JSONB field.

    Args:
        view: SavedView model instance

    Returns:
        SavedViewSchema
    """
    return SavedViewSchema(
        id=view.id,
        name=view.name,
        object_type=view.object_type,
        config=msgspec.convert(view.config, type=SavedViewConfigSchema),
        schema_version=view.schema_version,
        user_id=view.user_id,
        team_id=view.team_id,
        is_personal=view.is_personal,
        is_default=view.is_default,
        created_at=view.created_at,
        updated_at=view.updated_at,
    )


async def get_or_create_default_view(
    session: AsyncSession,
    *,
    user_id: int,
    object_type: ObjectTypes,
) -> SavedViewSchema:
    """Get user's default view or return hard-coded default.

    If user has a saved view marked as default, returns that view.
    Otherwise, returns a hard-coded default configuration.

    Hard-coded defaults have id=None to distinguish them from saved views.

    Args:
        session: Database session
        user_id: User ID
        object_type: Object type

    Returns:
        SavedViewSchema (either saved or hard-coded)
    """
    # Try to find user's default view
    stmt = select(SavedView).where(
        SavedView.object_type == object_type,
        SavedView.user_id == user_id,
        SavedView.is_default == True,  # noqa: E712
    )
    result = await session.execute(stmt)
    user_default = result.scalar_one_or_none()

    if user_default:
        return saved_view_to_schema(user_default)

    # Fall back to hard-coded default
    default_config = get_default_view_config(object_type)

    return SavedViewSchema(
        id=None,  # None indicates hard-coded default
        name=f"Default {object_type.value} View",
        object_type=object_type,
        config=default_config,
        schema_version=1,
        user_id=None,
        team_id=None,
        is_personal=False,
        is_default=True,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )
