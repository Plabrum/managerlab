from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import (
    ActionGroupType,
    BaseObjectAction,
    BaseTopLevelAction,
    action_group_factory,
)
from app.actions.base import EmptyActionData
from app.actions.deps import ActionDeps
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse, DownloadFileActionResult
from app.media.enums import MediaActions, MediaStates
from app.media.models import Media
from app.media.schemas import MediaUpdateSchema, RegisterMediaSchema
from app.utils.db import update_model

# Create media action group
media_actions = action_group_factory(
    ActionGroupType.MediaActions,
    model_type=Media,
)


@media_actions
class DeleteMedia(BaseObjectAction[Media, EmptyActionData]):
    action_key = MediaActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this media?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls, obj: Media, data: EmptyActionData, transaction: AsyncSession, deps
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted media",
        )


@media_actions
class UpdateMedia(BaseObjectAction[Media, MediaUpdateSchema]):
    action_key = MediaActions.update
    label = "Edit"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Media,
        data: MediaUpdateSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=deps.user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated media",
        )


@media_actions
class DownloadMedia(BaseObjectAction[Media, EmptyActionData]):
    action_key = MediaActions.download
    label = "Download"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.download

    @classmethod
    async def execute(
        cls, obj: Media, data: EmptyActionData, transaction: AsyncSession, deps
    ) -> ActionExecutionResponse:
        download_url = deps.s3_client.generate_presigned_download_url(key=obj.file_key, expires_in=3600)

        return ActionExecutionResponse(
            message="Download ready",
            action_result=DownloadFileActionResult(
                url=download_url,
                filename=obj.file_name,
            ),
        )

    @classmethod
    def is_available(cls, obj: Media | None, deps) -> bool:
        return obj is not None and obj.state == MediaStates.READY


@media_actions
class CreateMedia(BaseTopLevelAction[RegisterMediaSchema]):
    action_key = MediaActions.register
    label = "Create Media"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: RegisterMediaSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        file_type = "image" if data.mime_type.startswith("image/") else "video"
        media = Media(
            team_id=deps.team_id,
            campaign_id=deps.campaign_id,
            file_key=data.file_key,
            file_name=data.file_name,
            file_size=data.file_size,
            mime_type=data.mime_type,
            file_type=file_type,
            state=MediaStates.PENDING,
        )
        transaction.add(media)
        await transaction.flush()
        queue = deps.task_queues.get("default")
        await queue.enqueue("generate_thumbnail", media_id=int(media.id))
        return ActionExecutionResponse(
            message=f"Created media '{media.file_name}'",
        )
