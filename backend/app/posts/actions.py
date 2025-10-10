from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.base import BaseAction
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.registry import action_group_factory
from app.actions.schemas import ActionExecutionResponse
from app.posts.enums import PostStates, PostActions
from app.posts.models import Post
from app.posts.routes import PostUpdateDTO
from app.utils.dto import update_model

post_actions = action_group_factory(ActionGroupType.PostActions, model_type=Post)


@post_actions
class DeletePost(BaseAction):
    action_key = PostActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this post?"

    @classmethod
    async def execute(
        cls,
        obj: Post,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            success=True,
            message="Deleted post",
            results={},
        )


@post_actions
class UpdatePost(BaseAction):
    action_key = PostActions.update
    label = "Update"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Post,
        data: PostUpdateDTO,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        update_model(obj, data)
        transaction.add(obj)

        return ActionExecutionResponse(
            success=True,
            message="Updated post",
            results={},
        )


@post_actions
class PublishPost(BaseAction):
    """Publish a draft post."""

    action_key = PostActions.publish
    label = "Publish"
    is_bulk_allowed = True
    priority = 1
    icon = ActionIcon.send

    @classmethod
    async def execute(
        cls,
        obj: Post,
    ) -> ActionExecutionResponse:
        obj.state = PostStates.POSTED

        return ActionExecutionResponse(
            success=True,
            message="Published post",
            results={},
        )

    @classmethod
    def is_available(cls, obj: Post | None) -> bool:
        return obj is not None and obj.state == PostStates.DRAFT
