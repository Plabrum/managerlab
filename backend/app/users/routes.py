from typing import List

from litestar import Request, Router, get, post
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.users.models import User, WaitlistEntry, Team, Role
from app.users.objects import RosterObject, UserObject
from app.users.schemas import (
    CreateUserSchema,
    CreateTeamSchema,
    TeamDTO,
    UserDTO,
    UserWaitlistFormSchema,
    WaitlistEntryDTO,
)
from app.auth.guards import requires_user_id, requires_superuser
from app.users.enums import RoleLevel, UserStates

# Register objects (auto-registered via __init_subclass__, but explicit for clarity)
ObjectRegistry().register(ObjectTypes.Users, UserObject)
ObjectRegistry().register(ObjectTypes.Roster, RosterObject)


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

    return team


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
    ],
    tags=["users"],
)
