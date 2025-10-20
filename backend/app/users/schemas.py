from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from msgspec import Struct

from app.base.schemas import BaseSchema
from app.users.models import User, WaitlistEntry, Team
from app.users.enums import RoleLevel


from app.base.schemas import SanitizedSQLAlchemyDTO


class UserDTO(SanitizedSQLAlchemyDTO[User]):
    """Data transfer object for User model."""

    pass


class WaitlistEntryDTO(SQLAlchemyDTO[WaitlistEntry]):
    """Data transfer object for WaitlistEntry model."""

    pass


class TeamDTO(SanitizedSQLAlchemyDTO[Team]):
    """Data transfer object for Team model."""

    pass


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


class TeamListItemSchema(Struct):
    """Schema for a team in the list."""

    team_id: int
    team_name: str
    role_level: RoleLevel


class ListTeamsResponse(Struct):
    """Response for listing teams."""

    teams: list[TeamListItemSchema]
    current_team_id: int | None
    is_campaign_scoped: bool


class SwitchTeamRequest(Struct):
    """Request to switch team."""

    team_id: int
