from litestar.channels import ChannelsPlugin
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseObjectAction, action_group_factory
from app.actions.base import EmptyActionData
from app.actions.deps import ActionDeps
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.threads.enums import MessageActions, ThreadSocketMessageType
from app.threads.models import Message
from app.threads.schemas import MessageUpdateSchema, ServerMessage
from app.threads.services import notify_thread
from app.utils.sqids import sqid_encode

# Create message action group
message_actions = action_group_factory(
    ActionGroupType.MessageActions,
    model_type=Message,
)


@message_actions
class UpdateMessage(BaseObjectAction[Message, MessageUpdateSchema]):
    action_key = MessageActions.update
    label = "Edit"
    is_bulk_allowed = False
    priority = 10
    icon = ActionIcon.edit

    @classmethod
    def is_available(
        cls,
        obj: Message | None,
        deps: ActionDeps,
    ) -> bool:
        """Only message author can edit their message."""
        if not obj:
            return False
        return obj.user_id == deps.user

    @classmethod
    async def execute(
        cls,
        obj: Message,
        data: MessageUpdateSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # Update content
        obj.content = data.content
        transaction.add(obj)
        await transaction.flush()

        # Notify WebSocket subscribers
        await notify_thread(
            deps.channels,
            obj.thread_id,
            ServerMessage(
                message_type=ThreadSocketMessageType.MESSAGE_UPDATED,
                message_id=sqid_encode(obj.id),
                thread_id=sqid_encode(obj.thread_id),
                user_id=sqid_encode(obj.user_id or 0),
                viewers=[],  # Empty - actions don't have viewer_store access
            ),
        )

        return ActionExecutionResponse(
            message="Updated message",
        )


@message_actions
class DeleteMessage(BaseObjectAction[Message, EmptyActionData]):
    action_key = MessageActions.delete
    label = "Delete"
    is_bulk_allowed = False
    priority = 20
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this message?"
    should_redirect_to_parent = True

    @classmethod
    def is_available(
        cls,
        obj: Message | None,
        deps: ActionDeps,
    ) -> bool:
        """Only message author can delete their message."""
        if not obj:
            return False
        return obj.user_id == deps.user

    @classmethod
    async def execute(
        cls,
        obj: Message,
        data: EmptyActionData,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        # Soft delete
        obj.soft_delete()
        await transaction.flush()

        # Notify WebSocket subscribers
        await notify_thread(
            deps.channels,
            obj.thread_id,
            ServerMessage(
                message_type=ThreadSocketMessageType.MESSAGE_DELETED,
                message_id=sqid_encode(obj.id),
                thread_id=sqid_encode(obj.thread_id),
                user_id=sqid_encode(obj.user_id or 0),
                viewers=[],  # Empty - actions don't have viewer_store access
            ),
        )

        return ActionExecutionResponse(
            message="Deleted message",
        )
