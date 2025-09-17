from typing import List

from litestar import Router, get, post
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.dto import UserDTO
from app.users.models import User
from app.schemas.users import CreateUserSchema


@get("/", dto=UserDTO, return_dto=UserDTO)
async def list_users(transaction: AsyncSession) -> List[User]:
    """List all users."""
    result = await transaction.execute(select(User))
    users = result.scalars().all()
    return list(users)


@get("/{user_id:int}", dto=UserDTO, return_dto=UserDTO)
async def get_user(user_id: int, transaction: AsyncSession) -> User:
    """Get a user by ID."""
    stmt = select(User).where(User.id == user_id)
    result = await transaction.execute(stmt)
    user = result.scalar_one()
    return user


@post("/", return_dto=UserDTO)
async def create_user(data: CreateUserSchema, transaction: AsyncSession) -> User:
    """Create a new user."""
    user = User(email=data.email, name=data.name)
    transaction.add(user)
    return user


user_router = Router(
    path="/users",
    route_handlers=[list_users, get_user, create_user],
    tags=["users"],
)
