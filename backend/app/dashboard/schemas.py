"""Dashboard schemas for request/response handling."""

from typing import Any
from advanced_alchemy.extensions.litestar import SQLAlchemyDTOConfig

from app.base.schemas import BaseSchema, SanitizedSQLAlchemyDTO
from app.dashboard.models import Dashboard
from app.dashboard.enums import DashboardOwnerType


class DashboardDTO(SanitizedSQLAlchemyDTO[Dashboard]):
    """Data transfer object for Dashboard model."""

    config: SQLAlchemyDTOConfig = SQLAlchemyDTOConfig(
        max_nested_depth=0,
    )


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
