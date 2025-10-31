from litestar import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction, action_group_factory
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.base.models import BaseDBModel
from app.roster.enums import TopLevelRosterActions
from app.roster.models import Roster
from app.roster.schemas import RosterCreateSchema

top_level_roster_actions = action_group_factory(ActionGroupType.TopLevelRosterActions)


class RosterTopLevelActionMixin:
    """Mixin for roster top-level actions."""

    @classmethod
    def get_model(cls) -> type[BaseDBModel] | None:
        """Top-level actions don't operate on specific instances."""
        return None


@top_level_roster_actions
class CreateRoster(RosterTopLevelActionMixin, BaseAction):
    action_key = TopLevelRosterActions.create
    label = "Create Roster Member"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        obj: Roster,
        data: RosterCreateSchema,
        transaction: AsyncSession,
        request: Request,
        team_id: int,
    ) -> ActionExecutionResponse:
        # Get user_id from session
        user_id = request.session.get("user_id")
        if not user_id:
            return ActionExecutionResponse(
                message="User not authenticated",
            )

        # Create roster member
        roster = Roster(
            user_id=user_id,
            team_id=team_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            instagram_handle=data.instagram_handle,
        )
        transaction.add(roster)
        return ActionExecutionResponse(
            message="Created roster member",
        )
