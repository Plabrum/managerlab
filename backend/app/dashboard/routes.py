"""Dashboard routes for CRUD operations."""

from litestar import Request, Router, get, patch, post
from litestar.exceptions import NotFoundException, PermissionDeniedException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.auth.guards import requires_scoped_session
from app.dashboard.models import Dashboard, Widget
from app.dashboard.schemas import (
    CreateDashboardSchema,
    DashboardSchema,
    UpdateDashboardSchema,
    WidgetQuerySchema,
    WidgetSchema,
)
from app.utils.sqids import Sqid


def _widget_to_schema(widget: Widget, action_registry: ActionRegistry) -> WidgetSchema:
    """Convert Widget model to schema."""
    action_group = action_registry.get_class(ActionGroupType.WidgetActions)
    actions = action_group.get_available_actions(obj=widget)

    # Convert dict query to WidgetQuerySchema
    import msgspec

    query_schema = msgspec.convert(widget.query, type=WidgetQuerySchema)

    return WidgetSchema(
        id=widget.id,
        dashboard_id=Sqid(widget.dashboard_id),
        type=widget.type,
        title=widget.title,
        description=widget.description,
        query=query_schema,
        created_at=widget.created_at,
        updated_at=widget.updated_at,
        actions=actions,
    )


def _dashboard_to_schema(dashboard: Dashboard, action_registry: ActionRegistry) -> DashboardSchema:
    """Convert Dashboard model to schema."""
    # Compute actions for this dashboard
    action_group = action_registry.get_class(ActionGroupType.DashboardActions)
    actions = action_group.get_available_actions(obj=dashboard)

    # Convert widgets to schemas with their actions
    widgets = [_widget_to_schema(widget, action_registry) for widget in dashboard.widgets]

    return DashboardSchema(
        id=dashboard.id,
        name=dashboard.name,
        config=dashboard.config,
        user_id=dashboard.user_id,
        team_id=dashboard.team_id,
        is_default=dashboard.is_default,
        is_personal=dashboard.is_personal,
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at,
        widgets=widgets,
        actions=actions,
    )


@get("/")
async def list_dashboards(
    transaction: AsyncSession,
    request: Request,
    action_registry: ActionRegistry,
) -> list[DashboardSchema]:
    """List all dashboards accessible to the current user.

    Returns both personal dashboards (owned by the user) and team-wide dashboards.
    RLS automatically filters to the user's current team.
    """
    user_id: int = request.user

    # Query for both user's personal dashboards and team-wide dashboards
    # RLS will automatically filter to the current team
    stmt = (
        select(Dashboard)
        .where(
            or_(
                Dashboard.user_id == user_id,  # Personal dashboards
                Dashboard.user_id.is_(None),  # Team-wide dashboards
            )
        )
        .options(selectinload(Dashboard.widgets))
    )
    result = await transaction.execute(stmt)
    dashboards = result.scalars().all()

    return [_dashboard_to_schema(dashboard, action_registry) for dashboard in dashboards]


@get("/{id:str}")
async def get_dashboard(id: Sqid, transaction: AsyncSession, action_registry: ActionRegistry) -> DashboardSchema:
    """Get a specific dashboard by ID."""
    stmt = select(Dashboard).where(Dashboard.id == id).options(selectinload(Dashboard.widgets))
    result = await transaction.execute(stmt)
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise NotFoundException(f"Dashboard with id {id} not found")
    return _dashboard_to_schema(dashboard, action_registry)


@post("/")
async def create_dashboard(
    data: CreateDashboardSchema,
    request: Request,
    transaction: AsyncSession,
    team_id: int,
    action_registry: ActionRegistry,
) -> DashboardSchema:
    """Create a new dashboard.

    - Personal dashboards are visible only to the creating user within the team
    - Team-wide dashboards are visible to all team members
    """

    dashboard = Dashboard(
        name=data.name,
        config=data.config,
        user_id=request.user if data.is_personal else None,
        team_id=team_id,
        is_default=data.is_default,
    )
    transaction.add(dashboard)
    await transaction.flush()

    # Refresh with widgets relationship loaded
    await transaction.refresh(dashboard, attribute_names=["widgets"])
    return _dashboard_to_schema(dashboard, action_registry)


@patch("/{id:str}")
async def update_dashboard(
    id: Sqid,
    data: UpdateDashboardSchema,
    request: Request,
    transaction: AsyncSession,
    action_registry: ActionRegistry,
) -> DashboardSchema:
    """Update a dashboard's configuration.

    Users can update their personal dashboards.
    Team-wide dashboards can be updated by any team member.
    """
    # Eagerly load widgets to avoid lazy loading error
    stmt = select(Dashboard).where(Dashboard.id == id).options(selectinload(Dashboard.widgets))
    result = await transaction.execute(stmt)
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise NotFoundException(f"Dashboard with id {id} not found")

    # Verify user has access to this dashboard
    user_id: int = request.user

    # For personal dashboards, only the owner can update
    if dashboard.is_personal and dashboard.user_id != user_id:
        raise PermissionDeniedException("You can only update your own personal dashboards")

    # Apply updates
    if data.name is not None:
        dashboard.name = data.name
    if data.config is not None:
        dashboard.config = data.config
    if data.is_default is not None:
        dashboard.is_default = data.is_default

    await transaction.flush()
    return _dashboard_to_schema(dashboard, action_registry)


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
