"""Dashboard routes for CRUD operations."""

from litestar import Request, Router, get, patch, post
from litestar.exceptions import NotFoundException, PermissionDeniedException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guards import requires_scoped_session
from app.dashboard.enums import DashboardOwnerType
from app.dashboard.models import Dashboard
from app.dashboard.schemas import (
    CreateDashboardSchema,
    DashboardSchema,
    UpdateDashboardSchema,
)
from app.users.models import Role
from app.utils.db import get_or_404
from app.utils.sqids import Sqid


@get("/")
async def list_dashboards(
    transaction: AsyncSession,
    request: Request,
    team_id: int,
) -> list[DashboardSchema]:
    """List all dashboards accessible to the current user (personal + team dashboards)."""

    # Query for both user dashboards and team dashboards
    stmt = select(Dashboard).where(or_(Dashboard.user_id == request.user, Dashboard.team_id == team_id))
    result = await transaction.execute(stmt)
    dashboards = result.scalars().all()

    # Manually convert to DashboardSchema
    return [
        DashboardSchema(
            id=dashboard.id,
            name=dashboard.name,
            config=dashboard.config,
            owner_type=dashboard.owner_type,
            user_id=dashboard.user_id,
            team_id=dashboard.team_id,
            is_default=dashboard.is_default,
            created_at=dashboard.created_at,
            updated_at=dashboard.updated_at,
        )
        for dashboard in dashboards
    ]


@get("/{id:str}")
async def get_dashboard(id: Sqid, transaction: AsyncSession) -> DashboardSchema:
    dashboard = await get_or_404(transaction, Dashboard, id)
    return DashboardSchema(
        id=dashboard.id,
        name=dashboard.name,
        config=dashboard.config,
        owner_type=dashboard.owner_type,
        user_id=dashboard.user_id,
        team_id=dashboard.team_id,
        is_default=dashboard.is_default,
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at,
    )


@post("/")
async def create_dashboard(data: CreateDashboardSchema, request: Request, transaction: AsyncSession) -> DashboardSchema:
    """Create a new dashboard."""
    user_id: int = request.user

    # Validate owner type and IDs
    if data.owner_type == DashboardOwnerType.USER:
        # For user dashboards, use current user's ID
        actual_user_id = user_id
        actual_team_id = None
    elif data.owner_type == DashboardOwnerType.TEAM:
        if not data.team_id:
            raise ValueError("team_id is required for team dashboards")

        # Verify user is member of the team
        team_query = select(Role).where(Role.user_id == user_id, Role.team_id == data.team_id)
        team_result = await transaction.execute(team_query)
        if not team_result.scalar_one_or_none():
            raise PermissionDeniedException("You are not a member of this team")

        actual_user_id = None
        actual_team_id = data.team_id
    else:
        raise ValueError(f"Invalid owner_type: {data.owner_type}")

    dashboard = Dashboard(
        name=data.name,
        config=data.config,
        owner_type=data.owner_type,
        user_id=actual_user_id,
        team_id=actual_team_id,
        is_default=data.is_default,
    )
    transaction.add(dashboard)
    await transaction.flush()
    return DashboardSchema(
        id=dashboard.id,
        name=dashboard.name,
        config=dashboard.config,
        owner_type=dashboard.owner_type,
        user_id=dashboard.user_id,
        team_id=dashboard.team_id,
        is_default=dashboard.is_default,
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at,
    )


@patch("/{id:str}")
async def update_dashboard(
    id: Sqid,
    data: UpdateDashboardSchema,
    request: Request,
    transaction: AsyncSession,
) -> DashboardSchema:
    """Update a dashboard's configuration."""
    # id is already decoded from SQID string to int by msgspec
    dashboard = await transaction.get(Dashboard, id)

    if not dashboard:
        raise NotFoundException(f"Dashboard with id {id} not found")

    # Verify user has access to this dashboard
    user_id: int = request.user
    team_query = select(Role.team_id).where(Role.user_id == user_id)
    team_result = await transaction.execute(team_query)
    team_ids = [row[0] for row in team_result.all()]

    has_access = dashboard.user_id == user_id or (dashboard.team_id and dashboard.team_id in team_ids)

    if not has_access:
        raise PermissionDeniedException("You don't have access to this dashboard")

    # Apply updates
    if data.name is not None:
        dashboard.name = data.name
    if data.config is not None:
        dashboard.config = data.config
    if data.is_default is not None:
        dashboard.is_default = data.is_default

    await transaction.flush()
    return DashboardSchema(
        id=dashboard.id,
        name=dashboard.name,
        config=dashboard.config,
        owner_type=dashboard.owner_type,
        user_id=dashboard.user_id,
        team_id=dashboard.team_id,
        is_default=dashboard.is_default,
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at,
    )


# Dashboard router
dashboard_router = Router(
    path="/dashboards",
    guards=[requires_scoped_session],
    route_handlers=[
        list_dashboards,
        get_dashboard,
        create_dashboard,
        update_dashboard,
    ],
    tags=["dashboards"],
)
