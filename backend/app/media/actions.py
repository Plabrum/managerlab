from sqlalchemy.ext.asyncio import AsyncSession

from app.media.enums import MediaStates
from app.actions import BaseAction, action_group_factory, ActionGroupType
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse, DownloadFileActionResult
from app.client.s3_client import S3Client
from app.media.models import Media
from app.media.enums import MediaActions
from app.media.schemas import MediaUpdateSchema
from app.utils.db import update_model


# Create media action group
media_actions = action_group_factory(
    ActionGroupType.MediaActions,
    model_type=Media,
)


@media_actions
class DeleteMedia(BaseAction):
    action_key = MediaActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this media?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls,
        obj: Media,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted media",
        )


@media_actions
class UpdateMedia(BaseAction):
    action_key = MediaActions.update
    label = "Update"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Media,
        data: MediaUpdateSchema,
        transaction: AsyncSession,
        user: int,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated media",
        )


@media_actions
class DownloadMedia(BaseAction):
    action_key = MediaActions.download
    label = "Download"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.download

    @classmethod
    async def execute(
        cls,
        obj: Media,
        s3_client: S3Client,
    ) -> ActionExecutionResponse:
        download_url = s3_client.generate_presigned_download_url(
            key=obj.file_key, expires_in=3600
        )

        return ActionExecutionResponse(
            message="Download ready",
            action_result=DownloadFileActionResult(
                url=download_url,
                filename=obj.file_name,
            ),
        )

    @classmethod
    def is_available(cls, obj: Media | None) -> bool:
        return obj is not None and obj.state == MediaStates.READY
