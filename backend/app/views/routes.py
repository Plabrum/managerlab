"""View routes for CRUD operations."""

import msgspec
from litestar import Request, Router, delete, get, post
from litestar.exceptions import (
    NotFoundException,
    ValidationException,
)
from sqlalchemy import insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guards import requires_scoped_session
from app.objects.enums import ObjectTypes
from app.utils.db import get_or_404
from app.utils.sqids import Sqid
from app.views.models import SavedView
from app.views.schemas import (
    CreateSavedViewSchema,
    SavedViewSchema,
    UpdateSavedViewSchema,
)
from app.views.services import (
    check_view_ownership,
    clear_user_defaults,
    get_or_create_default_view,
    saved_view_to_schema,
)


@get("/{object_type:str}")
async def list_saved_views(
    object_type: ObjectTypes, transaction: AsyncSession, request: Request
) -> list[SavedViewSchema]:
    """List all saved views for a specific object type.

    Returns:
    - Personal views (owned by the user)
    - Team-shared views
    - System default view (ONLY if user hasn't set a personal default)

    RLS automatically filters to the user's current team.

    Returns full schemas including configuration, so clients don't need
    to make additional requests when switching between views.
    """
    # Query for both user's personal views and team-shared views for this object type
    # RLS will automatically filter to the current team
    # Order by: default first, then alphabetically by name
    stmt = (
        select(SavedView)
        .where(
            SavedView.object_type == object_type,
            or_(
                SavedView.user_id == request.user,  # Personal views
                SavedView.user_id.is_(None),  # Team-shared views
            ),
        )
        .order_by(
            SavedView.is_default.desc(),  # Default views first
            SavedView.name.asc(),  # Then alphabetically
        )
    )
    result = await transaction.execute(stmt)
    saved_views = result.scalars().all()

    # Convert to schemas
    view_schemas = [saved_view_to_schema(view) for view in saved_views]

    # Check if user has a personal default
    has_personal_default = any(v.is_default and v.is_personal for v in view_schemas)

    # If no personal default, include system default view at the beginning
    if not has_personal_default:
        system_default = await get_or_create_default_view(
            transaction,
            user_id=request.user,
            object_type=object_type,
        )
        # Only add if it's the hardcoded default (id=None)
        if system_default.id is None:
            view_schemas.insert(0, system_default)

    return view_schemas


@get("/{object_type:str}/{id:str}")
async def get_saved_view(
    object_type: ObjectTypes,
    id: Sqid,
    transaction: AsyncSession,
) -> SavedViewSchema:
    """Get a specific saved view by ID."""
    view = await get_or_404(transaction, SavedView, id)

    # Validate object_type matches
    if view.object_type != object_type:
        raise NotFoundException(f"SavedView {id} not found for object type {object_type}")

    return saved_view_to_schema(view)


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
        await clear_user_defaults(transaction, user_id=request.user, object_type=object_type)

    # Use INSERT...RETURNING to get timestamps in one query
    stmt = (
        insert(SavedView)
        .values(
            name=data.name,
            object_type=data.object_type,
            config=msgspec.structs.asdict(data.config),
            user_id=request.user if data.is_personal else None,
            team_id=team_id,
            is_default=data.is_default if data.is_personal else False,
        )
        .returning(SavedView)
    )
    result = await transaction.execute(stmt)
    view = result.scalar_one()

    return saved_view_to_schema(view)


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
    user_id: int = request.user

    view = await get_or_404(transaction, SavedView, id)

    # Validate object_type matches
    if view.object_type != object_type:
        raise NotFoundException(f"SavedView {id} not found for object type {object_type}")

    # Check permission to update this view
    check_view_ownership(view, user_id)

    # Handle is_default toggle
    if data.is_default is not None and data.is_default != view.is_default:
        if data.is_default:
            # Setting as default: clear other defaults first
            await clear_user_defaults(transaction, user_id=user_id, object_type=object_type)
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

    return saved_view_to_schema(view)


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
    view = await get_or_404(transaction, SavedView, id)

    # Validate object_type matches
    if view.object_type != object_type:
        raise NotFoundException(f"SavedView {id} not found for object type {object_type}")

    # Check permission to delete this view
    check_view_ownership(view, request.user)

    await transaction.delete(view)
    await transaction.flush()


# View router
view_router = Router(
    path="/views",
    guards=[requires_scoped_session],
    route_handlers=[
        list_saved_views,
        get_saved_view,
        create_saved_view,
        update_saved_view,
        delete_saved_view,
    ],
    tags=["views"],
)
