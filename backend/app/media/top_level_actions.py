from sqlalchemy.ext.asyncio import AsyncSession
from app.actions import BaseAction, action_group_factory, ActionGroupType
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.media.models import Media
from app.media.enums import TopLevelMediaActions
from app.media.schemas import MediaCreateDTO
from app.utils.dto import create_model


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
        cls, data: MediaCreateDTO, transaction: AsyncSession
    ) -> ActionExecutionResponse:
        new_media = create_model(Media, data)
        transaction.add(new_media)
        return ActionExecutionResponse(
            success=True,
            message=f"Created media '{new_media.file_name}'",
            results={"media_id": new_media.id},
        )
