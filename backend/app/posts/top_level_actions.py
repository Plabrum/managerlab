from typing import Any, Type
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction, action_group_factory
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.base.models import BaseDBModel
from app.posts.models import Post
from app.posts.enums import TopLevelPostActions
from app.posts.schemas import PostCreateSchema
from app.utils.db import create_model


top_level_post_actions = action_group_factory(ActionGroupType.TopLevelPostActions)


class PostTopLevelActionMixin:
    """Mixin for post top-level actions."""

    @classmethod
    def get_model(cls) -> Type[BaseDBModel] | None:
        """Top-level actions don't operate on specific instances."""
        return None


@top_level_post_actions
class CreatePost(PostTopLevelActionMixin, BaseAction):
    action_key = TopLevelPostActions.create
    label = "Create Post"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        obj: Post,
        data: PostCreateSchema,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        post = create_model(Post, data)
        transaction.add(post)
        return ActionExecutionResponse(
            success=True,
            message="Created post ",
            results={"post_id": post.id},
        )

    @classmethod
    def is_available(
        cls, obj: BaseDBModel, context: dict[str, Any] | None = None
    ) -> bool:
        return True
