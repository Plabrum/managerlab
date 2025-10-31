from litestar_saq import TaskQueues
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseAction, action_group_factory
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.media.enums import MediaStates, TopLevelMediaActions
from app.media.models import Media
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
        task_queues: TaskQueues,
        team_id: int | None = None,
        campaign_id: int | None = None,
    ) -> ActionExecutionResponse:
        file_type = "image" if data.mime_type.startswith("image/") else "video"
        media = Media(
            team_id=team_id,
            campaign_id=campaign_id,
            file_key=data.file_key,
            file_name=data.file_name,
            file_size=data.file_size,
            mime_type=data.mime_type,
            file_type=file_type,
            state=MediaStates.PENDING,
        )
        transaction.add(media)
        await transaction.flush()
        queue = task_queues.get("default")
        await queue.enqueue("generate_thumbnail", media_id=int(media.id))
        return ActionExecutionResponse(
            message=f"Created media '{media.file_name}'",
        )
