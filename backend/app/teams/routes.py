from litestar import Request, Router, get, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.auth.enums import ScopeType
from app.auth.guards import requires_session
from app.campaigns.models import Campaign
from app.teams.models import Team
from app.teams.schemas import (
    CreateTeamSchema,
    SwitchTeamRequest,
    SwitchTeamResponse,
    TeamListItemSchema,
    TeamSchema,
)
from app.users.enums import RoleLevel, UserStates
from app.users.models import Role, User
from app.utils.db import get_or_404
from app.utils.sqids import Sqid


@get("/{id:str}")
async def get_team(
    id: Sqid,
    request: Request,
    transaction: AsyncSession,
    action_registry: ActionRegistry,
) -> TeamSchema:
    """Get a team by ID with actions."""
    team = await get_or_404(
        transaction,
        Team,
        id,
        load_options=[
            selectinload(Team.roles),  # Needed for action availability checks
        ],
    )

    # Compute actions for this team
    action_group = action_registry.get_class(ActionGroupType.TeamActions)
    actions = action_group.get_available_actions(obj=team)

    return TeamSchema(
        id=team.id,
        name=team.name,
        description=team.description,
        created_at=team.created_at,
        updated_at=team.updated_at,
        actions=actions,
    )


@post("/", guards=[requires_session])
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
        actions=[],  # Create endpoint doesn't compute actions
    )


@get("/", guards=[requires_session])
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


# Teams router
team_router = Router(
    path="/teams",
    route_handlers=[
        list_teams,
        create_team,
        get_team,
    ],
    tags=["teams"],
)
