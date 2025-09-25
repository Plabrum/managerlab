from app.base.schemas import BaseSchema

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO

from app.base.schemas import SanitizedSQLAlchemyDTO
from app.users.models import User, WaitlistEntry


class UserDTO(SanitizedSQLAlchemyDTO[User]):
    """Data transfer object for User model."""

    pass


class WaitlistEntryDTO(SQLAlchemyDTO[WaitlistEntry]):
    """Data transfer object for WaitlistEntry model."""

    pass


class CreateUserSchema(BaseSchema):
    name: str
    email: str


class UserWaitlistFormSchema(BaseSchema):
    name: str
    email: str
    company: str | None = None
    message: str | None = None
