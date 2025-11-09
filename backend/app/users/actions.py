from litestar import Request
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.actions import ActionGroupType, BaseAction, action_group_factory
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.emails.service import EmailService
from app.users.enums import RoleLevel, TeamActions
from app.users.models import Role, Team
from app.users.schemas import InviteUserToTeamSchema
from app.users.utils import generate_scoped_team_link

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
    confirmation_message = (
        "Are you sure you want to delete this team? "
        "This action will soft-delete the team and it can be restored later by an administrator."
    )
    should_redirect_to_parent = False

    @classmethod
    def is_available(
        cls,
        obj: Team | None,
        **kwargs,
    ) -> bool:
        """Action is available if team exists and is not already deleted."""
        return obj is None or obj.is_deleted

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
            message="Team deleted successfully",
        )


@team_actions
class InviteUserToTeam(BaseAction):
    action_key = TeamActions.invite_user
    label = "Invite User"
    is_bulk_allowed = False
    priority = 50
    icon = ActionIcon.send
    confirmation_message = None
    should_redirect_to_parent = False

    @classmethod
    def is_available(
        cls,
        obj: Team | None,
        request: Request,
        **kwargs,
    ) -> bool:
        if obj is None or obj.is_deleted:
            return False

        user_id = request.user

        # Find the user's role from the loaded roles relationship
        # (Team must be loaded with selectinload(Team.roles) in the query)
        user_role = next((role for role in obj.roles if role.user_id == user_id), None)

        # Only ADMIN or OWNER can see this action
        return user_role is not None and user_role.role_level in (
            RoleLevel.ADMIN,
            RoleLevel.OWNER,
        )

    @classmethod
    async def execute(
        cls,
        obj: Team,
        data: InviteUserToTeamSchema,
        request: Request,
        transaction: AsyncSession,
        email_service: EmailService,
    ) -> ActionExecutionResponse:
        user_id = request.user

        # Query the user's role for this team (with user relationship eager-loaded for inviter name)
        stmt = (
            select(Role)
            .where(
                Role.user_id == user_id,
                Role.team_id == obj.id,
            )
            .options(selectinload(Role.user))
        )
        result = await transaction.execute(stmt)
        role = result.scalar_one()

        # Generate secure invitation link (expires in 72 hours)
        invitation_link = generate_scoped_team_link(
            team_id=int(obj.id),
            invited_email=data.email,
            expires_in_hours=72,
        )

        # Send invitation email
        await email_service.send_team_invitation_email(
            to_email=data.email,
            team_name=obj.name,
            inviter_name=role.user.name,
            invitation_link=invitation_link,
            expires_hours=72,
        )

        return ActionExecutionResponse(
            message=f"Invitation sent to {data.email}",
        )
