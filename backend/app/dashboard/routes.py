"""Dashboard routes for CRUD operations."""

from typing import List
from litestar import Router, Request, get, post, patch
from litestar.exceptions import NotFoundException, PermissionDeniedException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.dashboard.models import Dashboard
from app.dashboard.enums import DashboardOwnerType
from app.dashboard.schemas import (
    DashboardDTO,
    CreateDashboardSchema,
    UpdateDashboardSchema,
)
from app.users.models import Role
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_user_scope


@get("/", return_dto=DashboardDTO)
async def list_dashboards(
    request: Request, transaction: AsyncSession
) -> List[Dashboard]:
    """List all dashboards accessible to the current user (personal + team dashboards)."""
    user_id: int = request.user
    team_id: int | None = request.session.get("team_id")

    # Query for both user dashboards and team dashboards
    stmt = select(Dashboard).where(
        or_(Dashboard.user_id == user_id, Dashboard.team_id == team_id)
    )
    result = await transaction.execute(stmt)
    dashboards = result.scalars().all()
    return list(dashboards)


@get("/{id:str}", return_dto=DashboardDTO)
async def get_dashboard(
    id: Sqid, request: Request, transaction: AsyncSession
) -> Dashboard:
    """Get a specific dashboard by SQID."""
    dashboard_id = sqid_decode(id)
    dashboard = await transaction.get(Dashboard, dashboard_id)

    if not dashboard:
        raise NotFoundException(f"Dashboard with id {id} not found")

    # Verify user has access to this dashboard
    user_id: int = request.user
    team_query = select(Role.team_id).where(Role.user_id == user_id)
    team_result = await transaction.execute(team_query)
    team_ids = [row[0] for row in team_result.all()]

    has_access = dashboard.user_id == user_id or (
        dashboard.team_id and dashboard.team_id in team_ids
    )

    if not has_access:
        raise PermissionDeniedException("You don't have access to this dashboard")

    return dashboard


@post("/", return_dto=DashboardDTO)
async def create_dashboard(
    data: CreateDashboardSchema, request: Request, transaction: AsyncSession
) -> Dashboard:
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
        team_query = select(Role).where(
            Role.user_id == user_id, Role.team_id == data.team_id
        )
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
    return dashboard


@patch("/{id:str}", return_dto=DashboardDTO)
async def update_dashboard(
    id: Sqid,
    data: UpdateDashboardSchema,
    request: Request,
    transaction: AsyncSession,
) -> Dashboard:
    """Update a dashboard's configuration."""
    dashboard_id = sqid_decode(id)
    dashboard = await transaction.get(Dashboard, dashboard_id)

    if not dashboard:
        raise NotFoundException(f"Dashboard with id {id} not found")

    # Verify user has access to this dashboard
    user_id: int = request.user
    team_query = select(Role.team_id).where(Role.user_id == user_id)
    team_result = await transaction.execute(team_query)
    team_ids = [row[0] for row in team_result.all()]

    has_access = dashboard.user_id == user_id or (
        dashboard.team_id and dashboard.team_id in team_ids
    )

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
    return dashboard


# Dashboard router
dashboard_router = Router(
    path="/dashboards",
    guards=[requires_user_scope],
    route_handlers=[
        list_dashboards,
        get_dashboard,
        create_dashboard,
        update_dashboard,
    ],
    tags=["dashboards"],
)
