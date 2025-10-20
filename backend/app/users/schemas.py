from advanced_alchemy.extensions.litestar import SQLAlchemyDTO

from app.base.schemas import BaseSchema
from app.users.models import User, WaitlistEntry, Team


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
