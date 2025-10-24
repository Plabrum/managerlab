from datetime import datetime, date

from app.actions.schemas import ActionDTO
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


class WaitlistEntrySchema(BaseSchema):
    """Manual schema for WaitlistEntry model."""

    id: Sqid
    name: str
    email: str
    company: str | None
    message: str | None
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


class UserWaitlistFormSchema(BaseSchema):
    name: str
    email: str
    company: str | None = None
    message: str | None = None


class TeamListItemSchema(BaseSchema):
    """Schema for a team in the list."""

    team_id: int
    public_id: str  # Sqid-encoded ID for use with actions API
    team_name: str
    role_level: RoleLevel
    actions: list[ActionDTO] = []


class ListTeamsResponse(BaseSchema):
    """Response for listing teams."""

    teams: list[TeamListItemSchema]
    current_team_id: int | None
    is_campaign_scoped: bool


class SwitchTeamRequest(BaseSchema):
    """Request to switch team."""

    team_id: int


class RosterSchema(BaseSchema):
    """Schema for Roster model with all fields."""

    id: Sqid
    name: str
    email: str | None
    phone: str | None
    birthdate: date | None
    instagram_handle: str | None
    facebook_handle: str | None
    tiktok_handle: str | None
    youtube_channel: str | None
    profile_photo_id: int | None
    state: str
    created_at: datetime
    updated_at: datetime
    team_id: int | None
    actions: list[ActionDTO] = []


class RosterUpdateSchema(BaseSchema):
    """Schema for updating a roster member."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    birthdate: date | None = None
    instagram_handle: str | None = None
    facebook_handle: str | None = None
    tiktok_handle: str | None = None
    youtube_channel: str | None = None


class RosterCreateSchema(BaseSchema):
    """Schema for creating a new roster member."""

    name: str
    email: str | None = None
    phone: str | None = None
    instagram_handle: str | None = None
