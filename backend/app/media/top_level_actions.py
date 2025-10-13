from sqlalchemy.ext.asyncio import AsyncSession
from app.actions import BaseAction, action_group_factory, ActionGroupType
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.media.models import Media
from app.media.enums import TopLevelMediaActions
from app.media.schemas import RegisterMediaSchema


top_level_media_actions = action_group_factory(ActionGroupType.TopLevelMediaActions)


@top_level_media_actions
class CreateMedia(BaseAction):
    action_key = TopLevelMediaActions.create
    label = "Create Media"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: RegisterMediaSchema,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        file_type = "image" if data.mime_type.startswith("image/") else "video"
        new_media = Media(
            file_key=data.file_key,
            file_name=data.file_name,
            file_size=data.file_size,
            mime_type=data.mime_type,
            file_type=file_type,
            status="pending",
        )
        transaction.add(new_media)
        return ActionExecutionResponse(
            success=True,
            message=f"Created media '{new_media.file_name}'",
            results={"media_id": new_media.id},
        )
