"""Authentication-related routes and user management."""

from typing import Dict
from litestar import Router, get, post, delete
from litestar.connection import ASGIConnection
from litestar.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from msgspec import Struct

from app.auth.google.routes import google_auth_router
from app.users.models import User
from app.auth.guards import requires_verified_user, requires_superuser


class CurrentUserResponse(Struct):
    """Schema for current user information."""

    id: int
    name: str
    email: str
    email_verified: bool


@post("/logout")
async def logout_user(connection: ASGIConnection) -> Dict[str, str]:
    """Logout the current user by clearing the session."""
    connection.clear_session()
    return {"message": "Logged out successfully"}


@get("/profile", guards=[requires_verified_user])
async def get_user_profile(connection: ASGIConnection) -> CurrentUserResponse:
    """Get user profile - requires verified account."""
    user: User = connection.user
    return CurrentUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        email_verified=user.email_verified,
    )


@get("/admin/users", guards=[requires_superuser])
async def list_all_users(transaction: AsyncSession) -> list[CurrentUserResponse]:
    """Admin endpoint to list all users - requires superuser."""
    from sqlalchemy import select

    stmt = select(User)
    result = await transaction.execute(stmt)
    users = result.scalars().all()

    return [
        CurrentUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified=user.email_verified,
        )
        for user in users
    ]


@delete("/admin/users/{user_id:int}", guards=[requires_superuser], status_code=200)
async def delete_user(user_id: int, transaction: AsyncSession) -> Dict[str, str]:
    """Admin endpoint to delete a user - requires superuser."""
    from sqlalchemy import select

    stmt = select(User).where(User.id == user_id)
    result = await transaction.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await transaction.delete(user)
    return {"message": f"User {user.email} deleted successfully"}


# Authentication router
auth_router = Router(
    path="/auth",
    route_handlers=[
        logout_user,
        get_user_profile,
        list_all_users,
        delete_user,
        google_auth_router,
    ],
    tags=["auth"],
)
