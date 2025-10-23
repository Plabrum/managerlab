from typing import List

from litestar import Request, Router, get, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.users.models import User, WaitlistEntry, Team, Role
from app.users.objects import RosterObject, TeamObject, UserObject
from app.users.schemas import (
    CreateUserSchema,
    CreateTeamSchema,
    TeamDTO,
    UserDTO,
    UserWaitlistFormSchema,
    WaitlistEntryDTO,
    TeamListItemSchema,
    ListTeamsResponse,
    SwitchTeamRequest,
)
from app.auth.guards import requires_user_id, requires_superuser
from app.auth.enums import ScopeType
from app.users.enums import RoleLevel, UserStates
from app.campaigns.models import Campaign
from app.utils.sqids import sqid_encode

# Register objects (auto-registered via __init_subclass__, but explicit for clarity)
ObjectRegistry().register(ObjectTypes.Users, UserObject)
ObjectRegistry().register(ObjectTypes.Roster, RosterObject)
ObjectRegistry().register(ObjectTypes.Teams, TeamObject)


@get("/", dto=UserDTO, return_dto=UserDTO, guards=[requires_superuser])
async def list_users(transaction: AsyncSession) -> List[User]:
    """List all users - requires superuser privileges."""
    result = await transaction.execute(select(User))
    users = result.scalars().all()
    return list(users)


@get("/current_user", dto=UserDTO, return_dto=UserDTO)
async def get_current_user(request: Request, transaction: AsyncSession) -> User:
    """Get current authenticated user information."""
    user_id: int = request.user

    stmt = select(User).where(User.id == user_id)
    result = await transaction.execute(stmt)
    user = result.scalar_one()

    return user


@get("/{user_id:int}", dto=UserDTO, return_dto=UserDTO)
async def get_user(user_id: int, transaction: AsyncSession) -> User:
    """Get a user by ID - requires authentication."""
    stmt = select(User).where(User.id == user_id)
    result = await transaction.execute(stmt)
    user = result.scalar_one()
    return user


@post("/", return_dto=UserDTO, guards=[requires_superuser])
async def create_user(data: CreateUserSchema, transaction: AsyncSession) -> User:
    """Create a new user - requires superuser privileges."""
    user = User(email=data.email, name=data.name)
    transaction.add(user)
    return user


@post("/signup", return_dto=WaitlistEntryDTO, guards=[])
async def add_user_to_waitlist(
    data: UserWaitlistFormSchema,
    transaction: AsyncSession,
) -> WaitlistEntry:
    user = WaitlistEntry(
        email=data.email,
        name=data.name,
        company=data.company,
        message=data.message,
    )
    transaction.add(user)
    return user


@post("/teams", return_dto=TeamDTO, guards=[requires_user_id])
async def create_team(
    request: Request,
    data: CreateTeamSchema,
    transaction: AsyncSession,
) -> Team:
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
    stmt = select(User).where(User.id == user_id)
    result = await transaction.execute(stmt)
    user = result.scalar_one()

    if user.state == UserStates.NEEDS_TEAM:
        user.state = UserStates.ACTIVE

    # Set the session to use this team as the active scope
    request.session["scope_type"] = ScopeType.TEAM.value
    request.session["team_id"] = team.id

    return team


@get("/teams", guards=[requires_user_id])
async def list_teams(request: Request, transaction: AsyncSession) -> ListTeamsResponse:
    """List all teams for the current user.

    If user is in campaign scope, returns only the campaign's team (read-only).
    If user is in team scope or no scope, returns all teams they have access to.
    """
    user_id: int = request.user

    # Check if user is in campaign scope
    current_scope_type = request.session.get("scope_type")
    is_campaign_scoped = current_scope_type == ScopeType.CAMPAIGN.value

    if is_campaign_scoped:
        # User is in campaign scope - return only the campaign's team
        campaign_id = request.session.get("campaign_id")
        if not campaign_id:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Campaign scope is active but no campaign_id in session",
            )

        # Get the campaign's team
        stmt = (
            select(Campaign, Team)
            .join(Team, Campaign.team_id == Team.id)
            .where(Campaign.id == campaign_id, Team.deleted_at.is_(None))
        )
        result = await transaction.execute(stmt)
        row = result.one_or_none()

        if not row:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Campaign {campaign_id} not found",
            )

        campaign, team = row
        teams = [
            TeamListItemSchema(
                team_id=team.id,
                public_id=sqid_encode(team.id),
                team_name=team.name,
                role_level=RoleLevel.VIEWER,  # Campaign guests are treated as viewers
            )
        ]
        current_team_id = team.id
    else:
        # User is in team scope or no scope - return all teams via Role table
        team_stmt = (
            select(Role, Team)
            .join(Team, Role.team_id == Team.id)
            .where(Role.user_id == user_id, Team.deleted_at.is_(None))
        )
        team_result = await transaction.execute(team_stmt)
        rows = team_result.all()

        teams = [
            TeamListItemSchema(
                team_id=role.team_id,
                public_id=sqid_encode(role.team_id),
                team_name=team.name,
                role_level=role.role_level,
            )
            for role, team in rows
        ]
        current_team_id = request.session.get("team_id")

    return ListTeamsResponse(
        teams=teams,
        current_team_id=current_team_id,
        is_campaign_scoped=is_campaign_scoped,
    )


@post("/switch-team", guards=[requires_user_id])
async def switch_team(
    request: Request, data: SwitchTeamRequest, transaction: AsyncSession
) -> dict:
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
    request.session["team_id"] = data.team_id
    request.session.pop("campaign_id", None)  # Clear campaign_id if present

    return {"detail": "Switched to team", "team_id": data.team_id}


# Public router for waitlist signup (no authentication required)
public_user_router = Router(
    path="/users",
    route_handlers=[add_user_to_waitlist],
    tags=["users"],
)

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
