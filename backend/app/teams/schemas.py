from datetime import datetime

from app.actions.schemas import ActionDTO
from app.auth.enums import ScopeType
from app.base.schemas import BaseSchema
from app.utils.sqids import Sqid


class TeamSchema(BaseSchema):
    """Detail schema for Team domain object."""

    id: Sqid
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    actions: list[ActionDTO]  # Added for domain object pattern


class CreateTeamSchema(BaseSchema):
    """Schema for creating a new team."""

    name: str
    description: str | None = None


class TeamListItemSchema(BaseSchema):
    """Schema for a team in the list."""

    id: Sqid
    team_name: str
    scope_type: ScopeType
    is_selected: bool = False
    actions: list[ActionDTO] = []


class SwitchTeamRequest(BaseSchema):
    """Request to switch team."""

    team_id: Sqid


class SwitchTeamResponse(BaseSchema):
    """Response for switching team."""

    detail: str
    team_id: int


class InviteUserToTeamSchema(BaseSchema):
    """Schema for inviting a user to a team."""

    email: str
