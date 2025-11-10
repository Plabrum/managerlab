from datetime import datetime

from app.actions.schemas import ActionDTO
from app.auth.enums import ScopeType
from app.base.schemas import BaseSchema
from app.users.enums import RoleLevel
from app.utils.sqids import Sqid


class UserSchema(BaseSchema):
    """Manual schema for User model."""

    id: Sqid
    name: str
    email: str
    email_verified: bool
    state: str
    created_at: datetime
    updated_at: datetime


class TeamSchema(BaseSchema):
    """Manual schema for Team model."""

    id: Sqid
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class CreateUserSchema(BaseSchema):
    name: str
    email: str


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


class UserAndRoleSchema(BaseSchema):
    """Schema for a user with their role in a specific team context."""

    id: Sqid
    name: str
    email: str
    email_verified: bool
    state: str
    role_level: RoleLevel
    created_at: datetime
    updated_at: datetime
