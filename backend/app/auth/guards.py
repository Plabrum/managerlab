"""Authentication guards for route protection."""

import logging
from typing import TYPE_CHECKING

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers.base import BaseRouteHandler

from app.auth.enums import ScopeType
from app.auth.tokens import verify_payload_signature
from app.utils.configure import config

if TYPE_CHECKING:
    from litestar import Request

logger = logging.getLogger(__name__)


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


async def requires_webhook_signature(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that verifies HMAC-SHA256 webhook signature.

    Expects X-Webhook-Signature header with HMAC-SHA256 of request body.
    Uses WEBHOOK_SECRET from config for verification.

    Use this for public webhook endpoints that need to verify the sender's
    authenticity without requiring user authentication.

    Raises:
        NotAuthorizedException: If signature is missing or invalid.
    """
    from litestar import Request

    # Get signature from header
    signature = connection.headers.get("X-Webhook-Signature")
    if not signature:
        logger.warning("Webhook request missing X-Webhook-Signature header")
        raise NotAuthorizedException("Missing webhook signature")

    # Get request body (cast to Request to access body method)
    request = connection if isinstance(connection, Request) else None
    if request is None:
        raise NotAuthorizedException("Invalid connection type")

    body = await request.body()

    # Verify signature using constant-time comparison
    if not verify_payload_signature(body, signature, config.WEBHOOK_SECRET):
        logger.warning("Invalid webhook signature")
        raise NotAuthorizedException("Invalid webhook signature")

    logger.debug("Webhook signature verified successfully")
