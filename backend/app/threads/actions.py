"""Message actions."""

from litestar.channels import ChannelsPlugin
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction, action_group_factory, ActionGroupType
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.threads.models import Message
from app.threads.enums import MessageActions
from app.threads.schemas import MessageUpdateSchema
from app.threads.services import get_current_viewers_from_db, notify_thread
from app.threads.websocket_messages import MessageUpdateMessage, MessageUpdateType
from app.utils.sqids import Sqid as SqidType


# Create message action group
message_actions = action_group_factory(
    ActionGroupType.MessageActions,
    model_type=Message,
)


@message_actions
class UpdateMessage(BaseAction):
    action_key = MessageActions.update
    label = "Edit"
    is_bulk_allowed = False
    priority = 10
    icon = ActionIcon.edit

    @classmethod
    def is_available(
        cls,
        obj: Message | None,
        user_id: int,
        **kwargs,
    ) -> bool:
        """Only message author can edit their message."""
        if not obj:
            return False
        return obj.user_id == user_id

    @classmethod
    async def execute(
        cls,
        obj: Message,
        data: MessageUpdateSchema,
        transaction: AsyncSession,
        channels: ChannelsPlugin,
    ) -> ActionExecutionResponse:
        # Update content
        obj.content = data.content
        transaction.add(obj)
        await transaction.flush()

        # Get current viewers from DB
        viewers = await get_current_viewers_from_db(transaction, obj.thread_id)

        # Notify WebSocket subscribers
        await notify_thread(
            channels,
            obj.thread_id,
            MessageUpdateMessage(
                update_type=MessageUpdateType.UPDATED,
                message_id=SqidType(obj.id),
                thread_id=SqidType(obj.thread_id),
                user_id=SqidType(obj.user_id or 0),
            ),
            viewers,
        )

        return ActionExecutionResponse(
            message="Updated message",
        )


@message_actions
class DeleteMessage(BaseAction):
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
        user_id: int,
        **kwargs,
    ) -> bool:
        """Only message author can delete their message."""
        if not obj:
            return False
        return obj.user_id == user_id

    @classmethod
    async def execute(
        cls,
        obj: Message,
        transaction: AsyncSession,
        channels: ChannelsPlugin,
    ) -> ActionExecutionResponse:
        # Soft delete
        obj.soft_delete()
        await transaction.flush()

        # Get current viewers from DB
        viewers = await get_current_viewers_from_db(transaction, obj.thread_id)

        # Notify WebSocket subscribers
        await notify_thread(
            channels,
            obj.thread_id,
            MessageUpdateMessage(
                update_type=MessageUpdateType.DELETED,
                message_id=SqidType(obj.id),
                thread_id=SqidType(obj.thread_id),
                user_id=SqidType(obj.user_id or 0),
            ),
            viewers,
        )

        return ActionExecutionResponse(
            message="Deleted message",
        )
