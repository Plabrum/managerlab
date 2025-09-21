from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.users.models import User, WaitlistEntry


class UserDTO(SQLAlchemyDTO[User]):
    """Data transfer object for User model."""

    config = SQLAlchemyDTOConfig(exclude={"google_accounts"})


class WaitlistEntryDTO(SQLAlchemyDTO[WaitlistEntry]):
    """Data transfer object for WaitlistEntry model."""

    pass
