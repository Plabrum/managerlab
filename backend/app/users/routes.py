from litestar import Request, Router, get, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.enums import ScopeType
from app.auth.guards import requires_session, requires_team
from app.teams.schemas import SwitchTeamRequest, SwitchTeamResponse
from app.users.models import Role, User
from app.users.schemas import (
    UserAndRoleSchema,
    UserSchema,
)


@get("/", guards=[requires_team])
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


@post("/switch-team", guards=[requires_session])
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
    guards=[requires_session],
    route_handlers=[
        list_users,
        get_user,
        get_current_user,
        switch_team,
    ],
    tags=["users"],
)
