from typing import List

from litestar import Router, get, post
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.dto import UserDTO, WaitlistEntryDTO
from app.users.models import User, WaitlistEntry
from app.users.schemas import CreateUserSchema, UserWaitlistFormSchema
from app.auth.guards import requires_authenticated_user, requires_superuser


@get("/", dto=UserDTO, return_dto=UserDTO, guards=[requires_superuser])
async def list_users(transaction: AsyncSession) -> List[User]:
    """List all users - requires superuser privileges."""
    result = await transaction.execute(select(User))
    users = result.scalars().all()
    return list(users)


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
    data: UserWaitlistFormSchema, transaction: AsyncSession
) -> WaitlistEntry:
    user = WaitlistEntry(
        email=data.email,
        name=data.name,
        company=data.company,
        message=data.message,
    )
    transaction.add(user)
    return user


user_router = Router(
    path="/users",
    guards=[requires_authenticated_user],
    route_handlers=[list_users, get_user, create_user, add_user_to_waitlist],
    tags=["users"],
)
