from typing import Any

from app.actions.base import BaseAction
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.registry import action_group_factory
from app.actions.schemas import ActionExecutionResponse
from app.posts.enums import PostStates, PostActions
from app.posts.models import Post


# Create post action group
post_actions = action_group_factory(ActionGroupType.PostActions, model_type=Post)


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
    def is_available(
        cls, obj: Post | None, context: dict[str, Any] | None = None
    ) -> bool:
        """Publish is available for draft posts."""
        return obj is not None and obj.state == PostStates.DRAFT
