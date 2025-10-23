from litestar import Request
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import action_group_factory, ActionGroupType, BaseAction
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.users.enums import TeamActions, RoleLevel
from app.users.models import Team, Role


team_actions = action_group_factory(
    ActionGroupType.TeamActions,
    model_type=Team,
)


@team_actions
class DeleteTeam(BaseAction):
    action_key = TeamActions.delete
    label = "Delete Team"
    is_bulk_allowed = False
    priority = 100
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this team? This action will soft-delete the team and it can be restored later by an administrator."
    should_redirect_to_parent = False

    @classmethod
    def is_available(
        cls,
        obj: Team | None,
        **kwargs,
    ) -> bool:
        """Action is available if team exists and is not already deleted."""
        if obj is None or obj.is_deleted:
            return False
        return True

    @classmethod
    async def execute(
        cls,
        obj: Team,
        request: Request,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        """Execute team deletion. Only owners can delete teams."""
        user_id = request.user

        # Query the user's role for this team
        stmt = select(Role).where(
            Role.user_id == user_id,
            Role.team_id == obj.id,
        )
        result = await transaction.execute(stmt)
        role = result.scalar_one_or_none()

        # Only owners can delete teams
        if role is None or role.role_level != RoleLevel.OWNER:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Only team owners can delete teams",
            )

        obj.soft_delete()
        transaction.add(obj)
        return ActionExecutionResponse(
            success=True,
            message="Team deleted successfully",
            results={},
            should_redirect_to_parent=False,
        )
