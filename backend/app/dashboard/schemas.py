"""Dashboard schemas for request/response handling."""

from datetime import datetime
from typing import Any

from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
from app.utils.sqids import Sqid


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
