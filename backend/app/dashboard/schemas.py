"""Dashboard schemas for request/response handling."""

from datetime import datetime
from typing import Any

from app.base.schemas import BaseSchema
from app.dashboard.enums import DashboardOwnerType
from app.utils.sqids import Sqid


class DashboardSchema(BaseSchema):
    """Manual schema for Dashboard responses with explicit Sqid type."""

    id: Sqid
    name: str
    config: dict[str, Any]
    owner_type: DashboardOwnerType
    user_id: int | None
    team_id: int | None
    is_default: bool
    created_at: datetime
    updated_at: datetime


class CreateDashboardSchema(BaseSchema):
    """Schema for creating a new dashboard."""

    name: str
    config: dict[str, Any]
    owner_type: DashboardOwnerType
    user_id: int | None = None
    team_id: int | None = None
    is_default: bool = False


class UpdateDashboardSchema(BaseSchema):
    """Schema for updating a dashboard (partial updates)."""

    name: str | None = None
    config: dict[str, Any] | None = None
    is_default: bool | None = None
