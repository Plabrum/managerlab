from litestar import Request, Router, get, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.auth.enums import ScopeType
from app.auth.guards import requires_superuser, requires_user_id, requires_user_scope
from app.campaigns.models import Campaign
from app.users.enums import RoleLevel, UserStates
from app.users.models import Role, Team, User
from app.users.schemas import (
    CreateTeamSchema,
    CreateUserSchema,
    SwitchTeamRequest,
    SwitchTeamResponse,
    TeamListItemSchema,
    TeamSchema,
    UserAndRoleSchema,
    UserSchema,
)
from app.utils.db import get_or_404


@get("/", guards=[requires_user_scope])
async def list_users(
    transaction: AsyncSession,
    team_id: int,
) -> list[UserAndRoleSchema]:
    # Query users who are members of this team via Role table
    stmt = select(User, Role).where(Role.team_id == team_id).join(Role, Role.user_id == User.id)
    result = await transaction.execute(stmt)
    rows = result.all()

    return [
        UserAndRoleSchema(
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified=user.email_verified,
            state=user.state,
            role_level=role.role_level,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user, role in rows
    ]


@get("/current_user")
async def get_current_user(request: Request, transaction: AsyncSession) -> UserSchema:
    """Get current authenticated user information."""
    user_id: int = request.user

    stmt = select(User).where(User.id == user_id)
    result = await transaction.execute(stmt)
    user = result.scalar_one()

    return UserSchema(
        id=user.id,
        name=user.name,
        email=user.email,
        email_verified=user.email_verified,
        state=user.state,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@get("/{user_id:int}")
async def get_user(user_id: int, transaction: AsyncSession) -> UserSchema:
    """Get a user by ID - requires authentication."""
    stmt = select(User).where(User.id == user_id)
    result = await transaction.execute(stmt)
    user = result.scalar_one()
    return UserSchema(
        id=user.id,
        name=user.name,
        email=user.email,
        email_verified=user.email_verified,
        state=user.state,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@post("/", guards=[requires_superuser])
async def create_user(data: CreateUserSchema, transaction: AsyncSession) -> UserSchema:
    """Create a new user - requires superuser privileges."""
    user = User(email=data.email, name=data.name)
    transaction.add(user)
    await transaction.flush()
    return UserSchema(
        id=user.id,
        name=user.name,
        email=user.email,
        email_verified=user.email_verified,
        state=user.state,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@post("/teams", guards=[requires_user_id])
async def create_team(
    request: Request,
    data: CreateTeamSchema,
    transaction: AsyncSession,
) -> TeamSchema:
    """Create a new team and assign the current user as owner.

    This route requires authentication but NOT scope, as it's used during
    initial onboarding when a user doesn't have a team yet.
    """
    user_id: int = request.user

    # Create the team
    team = Team(name=data.name, description=data.description)
    transaction.add(team)
    await transaction.flush()  # Get team.id for role creation

    # Create owner role for the current user
    role = Role(user_id=user_id, team_id=team.id, role_level=RoleLevel.OWNER)
    transaction.add(role)

    # Update user state to ACTIVE if they were in NEEDS_TEAM state
    user = await get_or_404(transaction, User, user_id)

    if user.state == UserStates.NEEDS_TEAM:
        user.state = UserStates.ACTIVE

    # Set the session to use this team as the active scope
    request.session["scope_type"] = ScopeType.TEAM.value
    request.session["team_id"] = int(team.id)

    return TeamSchema(
        id=team.id,
        name=team.name,
        description=team.description,
        created_at=team.created_at,
        updated_at=team.updated_at,
    )


@get("/teams", guards=[requires_user_id])
async def list_teams(
    request: Request,
    transaction: AsyncSession,
    action_registry: ActionRegistry,
) -> list[TeamListItemSchema]:
    """List all teams for the current user.

    If user is in campaign scope, returns only the campaign's team (read-only).
    If user is in team scope or no scope, returns all teams they have access to.
    """
    user_id: int = request.user

    # Get the team actions group for populating actions
    team_action_group = action_registry.get_class(ActionGroupType.TeamActions)

    # Check if user is in campaign scope
    current_scope_type = request.session.get("scope_type")
    is_campaign_scoped = current_scope_type == ScopeType.CAMPAIGN.value

    if is_campaign_scoped:
        # User is in campaign scope - return only the campaign's team
        campaign_id: int | None = request.session.get("campaign_id")
        if not campaign_id:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Campaign scope is active but no campaign_id in session",
            )

        # Get the campaign and its team
        campaign = await get_or_404(transaction, Campaign, campaign_id)
        teams = [
            TeamListItemSchema(
                id=campaign.id,
                team_name=f"Guest Access: {campaign.name}",
                scope_type=ScopeType.CAMPAIGN,
                is_selected=True,
                actions=[],
            )
        ]
    else:
        # User is in team scope or no scope - return all teams via Role table
        team_id: int | None = request.session.get("team_id")
        if not team_id:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No team_id in session, cannot list teams",
            )

        result = await transaction.execute(
            select(Team)
            .join(Role, Role.team_id == Team.id)
            .where(Role.user_id == user_id, Team.deleted_at.is_(None))
            .options(selectinload(Team.roles))
        )

        teams = [
            TeamListItemSchema(
                id=team.id,
                team_name=team.name,
                scope_type=ScopeType.TEAM,
                is_selected=team.id == team_id,
                actions=team_action_group.get_available_actions(team),
            )
            for team in result.scalars().all()
        ]

    return teams


@post("/switch-team", guards=[requires_user_id])
async def switch_team(request: Request, data: SwitchTeamRequest, transaction: AsyncSession) -> SwitchTeamResponse:
    """Switch to a different team.

    Only allowed when not in campaign scope. Validates user has access to the team.
    """
    user_id: int = request.user

    # Check if user is in campaign scope
    current_scope_type = request.session.get("scope_type")
    if current_scope_type == ScopeType.CAMPAIGN.value:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Cannot switch teams while in campaign scope",
        )

    # Verify user has access to this team via Role table
    stmt = select(Role).where(Role.user_id == user_id, Role.team_id == data.team_id)
    result = await transaction.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"User does not have access to team {data.team_id}",
        )

    # Update session to team scope
    request.session["scope_type"] = ScopeType.TEAM.value
    request.session["team_id"] = int(data.team_id)
    request.session.pop("campaign_id", None)  # Clear campaign_id if present

    return SwitchTeamResponse(detail="Switched to team", team_id=data.team_id)


# Authenticated router for user management
user_router = Router(
    path="/users",
    guards=[requires_user_id],
    route_handlers=[
        list_users,
        get_user,
        create_user,
        create_team,
        get_current_user,
        list_teams,
        switch_team,
    ],
    tags=["users"],
)
