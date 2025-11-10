"""Authentication guards for route protection."""

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException
from litestar.handlers.base import BaseRouteHandler
from sqlalchemy import select

from app.auth.enums import ScopeType
from app.users.models import User


def requires_session(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires an authenticated user session.

    Use this for routes that need authentication but NOT scope:
    - Scope switching endpoints
    - Team/campaign creation
    - Initial onboarding flows
    - User profile management

    This does NOT check if user has selected a scope (team/campaign).

    Raises:
        NotAuthorizedException: If no user is authenticated.
    """
    if not connection.user:
        raise NotAuthorizedException("Authentication required")


def requires_team(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires user to have an active team scope.

    Use this for routes that specifically require team-level access:
    - Team settings and management
    - Team-wide reports
    - Team member management

    Raises:
        NotAuthorizedException: If no user is authenticated or team scope is not active.
    """
    user_id: int | None = connection.user
    if not user_id:
        raise NotAuthorizedException("Authentication required")

    scope_type = connection.session.get("scope_type")
    if scope_type != ScopeType.TEAM.value:
        raise NotAuthorizedException("Team scope required. Please switch to a team.")

    team_id = connection.session.get("team_id")
    if not team_id:
        raise NotAuthorizedException("Team scope is set but team_id is missing")


def requires_campaign(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires user to have an active campaign scope.

    Use this for routes that specifically require campaign-level access:
    - Campaign-specific deliverables
    - Campaign member views
    - Campaign-scoped reports

    Raises:
        NotAuthorizedException: If no user is authenticated or campaign scope is not active.
    """
    user_id: int | None = connection.user
    if not user_id:
        raise NotAuthorizedException("Authentication required")

    scope_type = connection.session.get("scope_type")
    if scope_type != ScopeType.CAMPAIGN.value:
        raise NotAuthorizedException("Campaign scope required. Please switch to a campaign.")

    campaign_id = connection.session.get("campaign_id")
    if not campaign_id:
        raise NotAuthorizedException("Campaign scope is set but campaign_id is missing")


def requires_scoped_session(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires user to have an active scope (team OR campaign).

    This is the default guard for most routes that access scoped resources.
    Use this when a route can work with either team or campaign scope.
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
