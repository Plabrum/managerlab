"""View routes for CRUD operations."""

from datetime import UTC, datetime

import msgspec
from litestar import Request, Router, delete, get, post
from litestar.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guards import requires_scoped_session
from app.objects.enums import ObjectTypes
from app.utils.sqids import Sqid
from app.views.defaults import get_default_view_config
from app.views.models import SavedView
from app.views.schemas import (
    CreateSavedViewSchema,
    SavedViewConfigSchema,
    SavedViewSchema,
    UpdateSavedViewSchema,
)


def _saved_view_to_schema(view: SavedView) -> SavedViewSchema:
    """Convert SavedView model to schema."""

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


async def _clear_user_defaults(
    transaction: AsyncSession,
    user_id: int,
    object_type: ObjectTypes,
) -> None:
    """Clear is_default flag on all user's views for the given object_type.

    This is called before setting a new default view to ensure only one view
    is marked as default per user per object_type.
    """
    stmt = (
        update(SavedView)
        .where(
            SavedView.user_id == user_id,
            SavedView.object_type == object_type,
            SavedView.is_default == True,
        )
        .values(is_default=False)
    )
    await transaction.execute(stmt)


@get("/{object_type:str}")
async def list_saved_views(
    object_type: ObjectTypes, transaction: AsyncSession, request: Request
) -> list[SavedViewSchema]:
    """List all saved views for a specific object type.

    Returns both personal views (owned by the user) and team-shared views.
    RLS automatically filters to the user's current team.

    Returns full schemas including configuration, so clients don't need
    to make additional requests when switching between views.
    """
    # Query for both user's personal views and team-shared views for this object type
    # RLS will automatically filter to the current team
    stmt = select(SavedView).where(
        SavedView.object_type == object_type,
        or_(
            SavedView.user_id == request.user,  # Personal views
            SavedView.user_id.is_(None),  # Team-shared views
        ),
    )
    result = await transaction.execute(stmt)
    views = result.scalars().all()

    return [_saved_view_to_schema(view) for view in views]


@get("/{object_type:str}/default")
async def get_default_view(
    object_type: ObjectTypes,
    transaction: AsyncSession,
    request: Request,
) -> SavedViewSchema:
    """Get the user's default view for this object type.

    If the user has a saved view marked as default, returns that view.
    Otherwise, returns a hard-coded default configuration.

    Hard-coded defaults have id=None to distinguish them from saved views.
    This endpoint always returns a view (never null/404).
    """
    user_id: int = request.user

    # Try to find user's default view
    stmt = select(SavedView).where(
        SavedView.object_type == object_type,
        SavedView.user_id == user_id,
        SavedView.is_default == True,  # noqa: E712
    )
    result = await transaction.execute(stmt)
    user_default = result.scalar_one_or_none()

    if user_default:
        return _saved_view_to_schema(user_default)

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


@get("/{object_type:str}/{id:str}")
async def get_saved_view(
    object_type: ObjectTypes,
    id: Sqid,
    transaction: AsyncSession,
) -> SavedViewSchema:
    """Get a specific saved view by ID."""
    stmt = select(SavedView).where(
        SavedView.id == id,
        SavedView.object_type == object_type,
    )
    result = await transaction.execute(stmt)
    view = result.scalar_one_or_none()
    if not view:
        raise NotFoundException(f"SavedView {id} not found for object type {object_type}")
    return _saved_view_to_schema(view)


@post("/{object_type:str}")
async def create_saved_view(
    object_type: ObjectTypes,
    data: CreateSavedViewSchema,
    request: Request,
    transaction: AsyncSession,
    team_id: int,
) -> SavedViewSchema:
    """Create a new saved view.

    - Personal views are visible only to the creating user within the team
    - Team-shared views are visible to all team members
    - Only personal views can be marked as default
    - Setting is_default=True clears other user defaults for this object_type
    """
    # Validate object_type matches path parameter
    if data.object_type != object_type:
        raise ValidationException(f"object_type in body ({data.object_type}) must match path parameter ({object_type})")
    # Validate: team-shared views cannot be default
    if data.is_default and not data.is_personal:
        raise ValidationException("Team-shared views cannot be marked as default")

    # Clear other defaults if setting this as default
    if data.is_default and data.is_personal:
        await _clear_user_defaults(transaction, request.user, object_type)

    view = SavedView(
        name=data.name,
        object_type=data.object_type,
        config=msgspec.structs.asdict(data.config),  # Convert msgspec Struct to dict
        user_id=request.user if data.is_personal else None,
        team_id=team_id,
        is_default=data.is_default if data.is_personal else False,
    )
    transaction.add(view)
    await transaction.flush()
    await transaction.refresh(view)

    return _saved_view_to_schema(view)


@post("/{object_type:str}/{id:str}", status_code=200)
async def update_saved_view(
    object_type: ObjectTypes,
    id: Sqid,
    data: UpdateSavedViewSchema,
    request: Request,
    transaction: AsyncSession,
) -> SavedViewSchema:
    """Update a saved view's name, configuration, or default status.

    Users can only update their own personal views.
    Team-shared views cannot be updated via this endpoint.

    Setting is_default=True will automatically clear other defaults for this object_type.
    """
    stmt = select(SavedView).where(
        SavedView.id == id,
        SavedView.object_type == object_type,
    )
    result = await transaction.execute(stmt)
    view = result.scalar_one_or_none()

    if not view:
        raise NotFoundException(f"SavedView {id} not found for object type {object_type}")

    # Verify user has permission to update this view
    user_id: int = request.user

    # For personal views, only the owner can update
    if view.is_personal and view.user_id != user_id:
        raise PermissionDeniedException("You can only update your own personal views")

    # For team-shared views, no updates allowed via this endpoint
    if view.is_team_shared:
        raise PermissionDeniedException("Team-shared views cannot be updated")

    # Handle is_default toggle
    if data.is_default is not None and data.is_default != view.is_default:
        if data.is_default:
            # Setting as default: clear other defaults first
            await _clear_user_defaults(transaction, user_id, object_type)
            view.is_default = True
        else:
            # Unsetting default
            view.is_default = False

    # Apply other updates
    if data.name is not None:
        view.name = data.name
    if data.config is not None:
        view.config = msgspec.structs.asdict(data.config)

    await transaction.flush()
    await transaction.refresh(view)

    return _saved_view_to_schema(view)


@delete("/{object_type:str}/{id:str}", status_code=204)
async def delete_saved_view(
    object_type: ObjectTypes,
    id: Sqid,
    request: Request,
    transaction: AsyncSession,
) -> None:
    """Delete a saved view.

    Users can only delete their own personal views.
    Team-shared views cannot be deleted via this endpoint.

    When a default view is deleted, the user will fall back to the hard-coded
    default on their next request to GET /{object_type}/default.
    """
    stmt = select(SavedView).where(
        SavedView.id == id,
        SavedView.object_type == object_type,
    )
    result = await transaction.execute(stmt)
    view = result.scalar_one_or_none()

    if not view:
        raise NotFoundException(f"SavedView {id} not found for object type {object_type}")

    # Verify user has permission to delete this view
    user_id: int = request.user

    # For personal views, only the owner can delete
    if view.is_personal and view.user_id != user_id:
        raise PermissionDeniedException("You can only delete your own personal views")

    # For team-shared views, no deletion allowed via this endpoint
    if view.is_team_shared:
        raise PermissionDeniedException("Team-shared views cannot be deleted")

    await transaction.delete(view)
    await transaction.flush()


# View router
view_router = Router(
    path="/views",
    guards=[requires_scoped_session],
    route_handlers=[
        list_saved_views,
        get_default_view,
        get_saved_view,
        create_saved_view,
        update_saved_view,
        delete_saved_view,
    ],
    tags=["views"],
)
