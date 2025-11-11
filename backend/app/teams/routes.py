import logging

from litestar import Request, Response, Router, get, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_302_FOUND, HTTP_400_BAD_REQUEST
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.auth.enums import ScopeType
from app.auth.guards import requires_session
from app.auth.models import TeamInvitationToken
from app.campaigns.models import Campaign
from app.teams.models import Team
from app.teams.schemas import (
    CreateTeamSchema,
    TeamListItemSchema,
    TeamSchema,
)
from app.teams.utils import verify_team_invitation_token
from app.users.enums import RoleLevel, UserStates
from app.users.models import Role, User
from app.utils.configure import config
from app.utils.db import get_or_404
from app.utils.sqids import Sqid

logger = logging.getLogger(__name__)


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
                is_selected=team.id == team_id if team_id else False,
                actions=team_action_group.get_available_actions(team),
            )
            for team in result.scalars().all()
        ]

    return teams


@get("/invitations/accept", guards=[])
async def accept_team_invitation(
    request: Request,
    transaction: AsyncSession,
    token: str,
) -> Response:
    """Accept a team invitation and create/link user to team.

    Args:
        request: Litestar request object
        transaction: Database session
        token: The invitation token from URL query parameter

    Returns:
        Redirect response to frontend

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not token:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Missing token parameter",
        )

    # Verify the invitation token
    invitation_data = await verify_team_invitation_token(transaction, token)

    if not invitation_data:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation. Please request a new invitation.",
        )

    team_id = invitation_data["team_id"]
    invited_email = invitation_data["invited_email"]

    # Check if user exists for this email
    user_stmt = select(User).where(User.email == invited_email)
    user_result = await transaction.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            email=invited_email,
            name=str(invited_email).split("@")[0],  # Use email prefix as default name
            email_verified=True,  # User proved they have access to the email by clicking the link
        )
        transaction.add(user)
        await transaction.flush()  # Flush to get user.id
        logger.info(f"Created new user {user.id} from team invitation (email={invited_email})")
    else:
        # Mark email as verified (user proved they have access to the email)
        if not user.email_verified:
            user.email_verified = True
            logger.info(f"Marked user {user.id} email as verified via team invitation")

    # Check if user is already in this team
    role_check_stmt = select(Role).where(
        Role.user_id == user.id,
        Role.team_id == team_id,
    )
    role_check_result = await transaction.execute(role_check_stmt)
    existing_role = role_check_result.scalar_one_or_none()

    if existing_role:
        logger.warning(f"User {user.id} already has role in team {team_id}, continuing anyway")
    else:
        # Create role linking user to team (default: MEMBER)
        role = Role(
            user_id=user.id,
            team_id=team_id,
            role_level=RoleLevel.MEMBER,
        )
        transaction.add(role)
        logger.info(f"Added user {user.id} to team {team_id} as MEMBER")

    # Update user state to ACTIVE if they were in NEEDS_TEAM state
    if user.state == UserStates.NEEDS_TEAM:
        user.state = UserStates.ACTIVE
        logger.info(f"Updated user {user.id} state to ACTIVE")

    # Mark invitation as accepted (with lock to prevent race conditions)
    from app.auth.tokens import hash_token as hash_token_func

    token_hash = hash_token_func(token)
    invitation_stmt = (
        select(TeamInvitationToken)
        .where(TeamInvitationToken.token_hash == token_hash)
        .with_for_update()  # Lock to prevent concurrent acceptance
    )
    invitation_result = await transaction.execute(invitation_stmt)
    invitation_token = invitation_result.scalar_one_or_none()

    if invitation_token:
        invitation_token.mark_as_accepted()
        logger.info(f"Marked invitation token as accepted for user {user.id} joining team {team_id}")

    # Create secure session (same as OAuth and magic link)
    request.session["user_id"] = int(user.id)
    request.session["authenticated"] = True
    request.session["scope_type"] = ScopeType.TEAM.value
    request.session["team_id"] = int(team_id)

    # Redirect to frontend success page
    frontend_url = config.SUCCESS_REDIRECT_URL

    logger.info(f"User {user.id} accepted team {team_id} invitation, redirecting to {frontend_url}")
    return Response(
        content="",
        status_code=HTTP_302_FOUND,
        headers={"Location": frontend_url},
    )


# Teams router
team_router = Router(
    path="/teams",
    route_handlers=[
        list_teams,
        create_team,
        get_team,
        accept_team_invitation,
    ],
    tags=["teams"],
)
