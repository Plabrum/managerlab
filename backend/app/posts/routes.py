from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.posts.models import Post
from app.base.schemas import SanitizedSQLAlchemyDTO, UpdateSQLAlchemyDTO
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_authenticated_user

# Register PostObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.posts.object import PostObject

ObjectRegistry.register(ObjectTypes.Posts, PostObject)


class PostDTO(SanitizedSQLAlchemyDTO[Post]):
    """Data transfer object for Post model."""

    pass


class PostUpdateDTO(UpdateSQLAlchemyDTO[Post]):
    """DTO for partial Post updates."""

    pass


@get("/{id:str}", return_dto=PostDTO)
async def get_post(id: Sqid, transaction: AsyncSession) -> Post:
    """Get a post by SQID."""
    post_id = sqid_decode(id)
    post = await transaction.get(Post, post_id)
    if not post:
        raise ValueError(f"Post with id {id} not found")
    return post


@post("/{id:str}", return_dto=PostDTO)
async def update_post(id: Sqid, data: PostUpdateDTO, transaction: AsyncSession) -> Post:
    """Update a post by SQID."""
    post_id = sqid_decode(id)
    post = await transaction.get(Post, post_id)
    if not post:
        raise ValueError(f"Post with id {id} not found")

    # Apply updates from DTO - partial=True means only provided fields are included
    for field, value in data.__dict__.items():
        if hasattr(post, field):  # Only update existing model fields
            setattr(post, field, value)

    await transaction.flush()
    return post


# Post router
post_router = Router(
    path="/posts",
    guards=[requires_authenticated_user],
    route_handlers=[
        get_post,
        update_post,
    ],
    tags=["posts"],
)
