from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.posts.models import Post
from app.posts.schemas import PostDTO, PostUpdateSchema
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model


@get("/{id:str}", return_dto=PostDTO)
async def get_post(id: Sqid, transaction: AsyncSession) -> Post:
    """Get a post by SQID."""
    post_id = sqid_decode(id)
    return await get_or_404(transaction, Post, post_id)


@post("/{id:str}", return_dto=PostDTO)
async def update_post(
    id: Sqid, data: PostUpdateSchema, transaction: AsyncSession
) -> Post:
    """Update a post by SQID."""
    post_id = sqid_decode(id)
    post = await get_or_404(transaction, Post, post_id)
    update_model(post, data)
    await transaction.flush()
    return post


# Post router
post_router = Router(
    path="/posts",
    guards=[requires_user_id],
    route_handlers=[
        get_post,
        update_post,
    ],
    tags=["posts"],
)
