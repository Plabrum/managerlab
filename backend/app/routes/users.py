from typing import List

from litestar import Router, get, post
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.status_codes import HTTP_201_CREATED
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.users import CreateUserSchema


class UserDTO(SQLAlchemyDTO[User]):
    """Data transfer object for User model."""

    pass


# @get("/", dto=UserDTO, return_dto=UserDTO)
# async def list_users(transaction: AsyncSession) -> List[User]:
#     """List all users."""
#     stmt = select(User)
#     result = await db_session.execute(stmt)
#     users = result.scalars().all()
#     return list(users)


@get("/")
async def list_users(transaction: AsyncSession) -> str:
    """List all users with error handling."""
    try:
        stmt = select(User)
        result = await transaction.execute(stmt)
        users = result.scalars().all()
        return f"Success: Found {str(users)} users"
    except Exception as e:
        import traceback

        error_detail = (
            f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        )
        return error_detail


@get("/{user_id:int}", dto=UserDTO, return_dto=UserDTO)
async def get_user(user_id: int, transaction: AsyncSession) -> User:
    """Get a user by ID."""
    stmt = select(User).where(User.id == user_id)
    result = await transaction.execute(stmt)
    user = result.scalar_one()
    return user


@post("/", status_code=HTTP_201_CREATED, return_dto=UserDTO)
async def create_user(
    data: CreateUserSchema, transaction: AsyncSession
) -> User:
    """Create a new user."""
    user = User(email=data.email, name=data.name)
    transaction.add(user)
    await transaction.commit()
    await transaction.refresh(user)
    return user


user_router = Router(
    path="/users",
    route_handlers=[list_users, get_user, create_user],
    tags=["users"],
)
