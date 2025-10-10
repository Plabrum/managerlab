from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from app.base.schemas import (
    SanitizedSQLAlchemyDTO,
    UpdateSQLAlchemyDTO,
)
from app.posts.models import Post


class PostDTO(SanitizedSQLAlchemyDTO[Post]):
    pass


class PostUpdateDTO(UpdateSQLAlchemyDTO[Post]):
    pass


# class PostCreateDTO(CreateSQLAlchemyDTO[Post]):
# pass
class PostCreateDTO(SQLAlchemyDTO[Post]):
    config = SQLAlchemyDTOConfig(exclude={"id"})
