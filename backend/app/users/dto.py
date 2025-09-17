from advanced_alchemy.extensions.litestar import SQLAlchemyDTO

from app.users.models import User


class UserDTO(SQLAlchemyDTO[User]):
    """Data transfer object for User model."""

    pass
