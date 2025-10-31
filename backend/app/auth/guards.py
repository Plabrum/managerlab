"""Authentication guards for route protection."""

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException
from litestar.handlers.base import BaseRouteHandler
from sqlalchemy import select

from app.auth.enums import ScopeType
from app.users.models import User


def requires_user_id(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires an authenticated user (user_id in session).

    Use this for routes that need authentication but NOT scope:
    - Scope switching endpoints
    - Business/team creation
    - Initial onboarding flows

    This does NOT check if user has selected a scope (team/campaign).

    Raises:
        NotAuthorizedException: If no user is authenticated.
    """
    if not connection.user:
        raise NotAuthorizedException("Authentication required")


def requires_user_scope(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires user to have an active scope (team or campaign).

    Use this for most routes that access scoped resources.
    Ensures RLS session variables will be set properly.

    With RLS enabled, queries will fail or return empty without a scope set.

    Raises:
        NotAuthorizedException: If no user is authenticated or no scope is set.
    """
    user_id: int | None = connection.user
    if not user_id:
        raise NotAuthorizedException("Authentication required")

    scope_type = connection.session.get("scope_type")
    if not scope_type:
        raise NotAuthorizedException("No active scope. Please select a team or campaign to continue.")

    # Validate that we have the corresponding ID
    if scope_type == ScopeType.TEAM.value:
        team_id = connection.session.get("team_id")
        if not team_id:
            raise NotAuthorizedException("Team scope is set but team_id is missing")
    elif scope_type == ScopeType.CAMPAIGN.value:
        campaign_id = connection.session.get("campaign_id")
        if not campaign_id:
            raise NotAuthorizedException("Campaign scope is set but campaign_id is missing")


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
