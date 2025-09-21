"""Authentication guards for route protection."""

from litestar.connection import ASGIConnection
from litestar.exceptions import PermissionDeniedException, NotAuthorizedException
from litestar.handlers.base import BaseRouteHandler
from sqlalchemy import select

from app.users.models import User


def requires_authenticated_user(
    connection: ASGIConnection, _: BaseRouteHandler
) -> None:
    """Guard that requires an authenticated user.

    Raises:
        NotAuthorizedException: If no user is authenticated.
    """
    if not connection.user:
        raise NotAuthorizedException("Authentication required")


async def requires_active_user(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires an active user account.

    Raises:
        NotAuthorizedException: If no user is authenticated.
        PermissionDeniedException: If user account is not active.
    """
    user_id: int | None = connection.user

    if not user_id:
        raise NotAuthorizedException("Authentication required")

    # For now, all users are considered active since we don't have an active field
    # This can be extended when we add user account status fields
    # To check user properties, we would need to load from database:
    # async with connection.app.plugins.get(SQLAlchemyPlugin).get_session() as db_session:
    #     stmt = select(User).where(User.id == user_id)
    #     result = await db_session.execute(stmt)
    #     user = result.scalar_one_or_none()
    #     if not user or not user.is_active:
    #         raise PermissionDeniedException("Account is not active")


async def requires_verified_user(
    connection: ASGIConnection, _: BaseRouteHandler
) -> None:
    """Guard that requires a verified user account.

    Raises:
        NotAuthorizedException: If no user is authenticated.
        PermissionDeniedException: If user account is not verified.
    """
    user_id: int | None = connection.user

    if not user_id:
        raise NotAuthorizedException("Authentication required")

    # Need to load user from database to check email_verified
    from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin

    sqlalchemy_plugin = connection.app.plugins.get(SQLAlchemyPlugin)
    if not sqlalchemy_plugin:
        raise NotAuthorizedException("Database connection required")

    async with sqlalchemy_plugin.get_session() as db_session:
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise NotAuthorizedException("User not found")

        if not user.email_verified:
            raise PermissionDeniedException("Email verification required")


async def requires_superuser(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires superuser privileges.

    Raises:
        NotAuthorizedException: If no user is authenticated.
        PermissionDeniedException: If user is not a superuser.
    """
    user_id: int | None = connection.user

    if not user_id:
        raise NotAuthorizedException("Authentication required")

    # Need to load user from database to check email
    from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin

    sqlalchemy_plugin = connection.app.plugins.get(SQLAlchemyPlugin)
    if not sqlalchemy_plugin:
        raise NotAuthorizedException("Database connection required")

    async with sqlalchemy_plugin.get_session() as db_session:
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise NotAuthorizedException("User not found")

        # For now, check if user has superuser email patterns
        # This can be extended when we add proper role/permission system
        superuser_emails = ["admin@manageros.com", "support@manageros.com"]

        if user.email not in superuser_emails:
            raise PermissionDeniedException("Superuser privileges required")
