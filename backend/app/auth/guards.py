"""Authentication guards for route protection."""

from litestar.connection import ASGIConnection
from litestar.exceptions import PermissionDeniedException, NotAuthorizedException
from litestar.handlers.base import BaseRouteHandler
from sqlalchemy import select

from app.users.models import User, Role
from app.campaigns.models import CampaignGuest


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
    # async with connection.app.plugins.get(SQLAlchemyPlugin).get_session() as session:
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

    assert isinstance(sqlalchemy_plugin, SQLAlchemyPlugin)  # Type narrowing for mypy
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

    assert isinstance(sqlalchemy_plugin, SQLAlchemyPlugin)  # Type narrowing for mypy
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


async def requires_team_scope(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires team scope.

    Validates that the user is authenticated and has team scope active.
    Verifies the user has access to the team via Role table.

    Raises:
        NotAuthorizedException: If no user is authenticated or scope not set.
        PermissionDeniedException: If scope is not 'team' or user lacks team access.
    """
    user_id: int | None = connection.user
    if not user_id:
        raise NotAuthorizedException("Authentication required")

    scope_type = connection.session.get("scope_type")
    if scope_type != "team":
        raise PermissionDeniedException("Team scope required - please switch to a team")

    team_id = connection.session.get("team_id")
    if not team_id:
        raise NotAuthorizedException("Team ID not found in session")

    # Verify user has access to this team via Role table
    from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin

    sqlalchemy_plugin = connection.app.plugins.get(SQLAlchemyPlugin)
    if not sqlalchemy_plugin:
        raise NotAuthorizedException("Database connection required")

    async with sqlalchemy_plugin.get_session() as db_session:
        stmt = select(Role).where(Role.user_id == user_id, Role.team_id == team_id)
        result = await db_session.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            raise PermissionDeniedException(
                f"User does not have access to team {team_id}"
            )


async def requires_campaign_scope(
    connection: ASGIConnection, _: BaseRouteHandler
) -> None:
    """Guard that requires campaign scope.

    Validates that the user is authenticated and has campaign scope active.
    Verifies the user has access to the campaign via CampaignGuest table.

    Raises:
        NotAuthorizedException: If no user is authenticated or scope not set.
        PermissionDeniedException: If scope is not 'campaign' or user lacks campaign access.
    """
    user_id: int | None = connection.user
    if not user_id:
        raise NotAuthorizedException("Authentication required")

    scope_type = connection.session.get("scope_type")
    if scope_type != "campaign":
        raise PermissionDeniedException(
            "Campaign scope required - please switch to a campaign"
        )

    campaign_id = connection.session.get("campaign_id")
    if not campaign_id:
        raise NotAuthorizedException("Campaign ID not found in session")

    # Verify user has access to this campaign via CampaignGuest table
    from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin

    sqlalchemy_plugin = connection.app.plugins.get(SQLAlchemyPlugin)
    if not sqlalchemy_plugin:
        raise NotAuthorizedException("Database connection required")

    async with sqlalchemy_plugin.get_session() as db_session:
        stmt = select(CampaignGuest).where(
            CampaignGuest.user_id == user_id, CampaignGuest.campaign_id == campaign_id
        )
        result = await db_session.execute(stmt)
        guest = result.scalar_one_or_none()

        if not guest:
            raise PermissionDeniedException(
                f"User does not have access to campaign {campaign_id}"
            )


async def requires_any_scope(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that accepts either team or campaign scope.

    Validates that the user is authenticated and has some scope active.
    Use this for routes that work with both team and campaign scoped resources.

    Raises:
        NotAuthorizedException: If no user is authenticated or scope not set.
    """
    user_id: int | None = connection.user
    if not user_id:
        raise NotAuthorizedException("Authentication required")

    scope_type = connection.session.get("scope_type")
    if not scope_type:
        raise NotAuthorizedException("Scope not set - please select a team or campaign")

    # Validate the appropriate scope based on type
    if scope_type == "team":
        await requires_team_scope(connection, _)
    elif scope_type == "campaign":
        await requires_campaign_scope(connection, _)
    else:
        raise NotAuthorizedException(f"Invalid scope_type: {scope_type}")
