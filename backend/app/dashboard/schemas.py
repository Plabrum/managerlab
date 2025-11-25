"""Dashboard schemas for request/response handling."""

from datetime import datetime
from typing import Any

from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
from app.utils.sqids import Sqid

# =============================================================================
# Widget Schemas
# =============================================================================


class WidgetSchema(BaseSchema):
    """Response schema for Widget."""

    id: Sqid
    dashboard_id: Sqid
    type: str
    title: str
    description: str | None
    query: dict[str, Any]
    position_x: int
    position_y: int
    size_w: int
    size_h: int
    created_at: datetime
    updated_at: datetime
    actions: list[ActionDTO]


class CreateWidgetSchema(BaseSchema):
    """Schema for creating a widget."""

    dashboard_id: Sqid
    type: str  # bar_chart, line_chart, pie_chart, stat_number
    title: str
    description: str | None = None
    query: dict[str, Any] = {}
    position_x: int = 0
    position_y: int = 0
    size_w: int = 1
    size_h: int = 1


class EditWidgetSchema(BaseSchema):
    """Schema for updating a widget (partial updates)."""

    type: str | None = None
    title: str | None = None
    description: str | None = None
    query: dict[str, Any] | None = None
    position_x: int | None = None
    position_y: int | None = None
    size_w: int | None = None
    size_h: int | None = None


class WidgetPositionSchema(BaseSchema):
    """Position and size data for a single widget during reorder/resize."""

    id: Sqid
    position_x: int
    position_y: int
    size_w: int | None = None
    size_h: int | None = None


class ReorderWidgetsSchema(BaseSchema):
    """Schema for reordering widgets (batch position update)."""

    dashboard_id: Sqid
    widgets: list[WidgetPositionSchema]


# =============================================================================
# Dashboard Schemas
# =============================================================================


class DashboardSchema(BaseSchema):
    """Manual schema for Dashboard responses with explicit Sqid type."""

    id: Sqid
    name: str
    config: dict[str, Any]
    user_id: int | None  # NULL = team-wide, set = personal dashboard
    team_id: int
    is_default: bool
    is_personal: bool  # Convenience field
    created_at: datetime
    updated_at: datetime
    widgets: list[WidgetSchema]  # Widgets within this dashboard
    actions: list[ActionDTO]


class CreateDashboardSchema(BaseSchema):
    """Schema for creating a new dashboard.

    - To create a personal dashboard: set is_personal=True (user_id will be set automatically)
    - To create a team-wide dashboard: set is_personal=False or omit it
    """

    name: str
    config: dict[str, Any] = {}
    is_personal: bool = False  # If True, dashboard is personal to the creating user
    is_default: bool = False


class UpdateDashboardSchema(BaseSchema):
    """Schema for updating a dashboard (partial updates)."""

    name: str | None = None
    config: dict[str, Any] | None = None
    is_default: bool | None = None
