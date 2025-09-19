from advanced_alchemy.extensions.litestar import SQLAlchemyDTO

from app.users.models import User, WaitlistEntry


class UserDTO(SQLAlchemyDTO[User]):
    """Data transfer object for User model."""

    pass


class WaitlistEntryDTO(SQLAlchemyDTO[WaitlistEntry]):
    """Data transfer object for WaitlistEntry model."""

    pass
