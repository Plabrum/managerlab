from typing import Any

from app.actions import BaseAction, action_group_factory, ActionGroupType
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.client.s3_client import S3Client
from app.media.models import Media
from app.media.enums import MediaActions


# Create media action group
media_actions = action_group_factory(ActionGroupType.MediaActions, model_type=Media)


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
            success=True,
            message="Download URL generated",
            results={
                "download_url": download_url,
                "file_name": obj.file_name,
            },
        )

    @classmethod
    def is_available(
        cls, obj: Media | None, context: dict[str, Any] | None = None
    ) -> bool:
        return obj is not None and obj.status == "ready"
