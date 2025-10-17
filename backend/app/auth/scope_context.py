"""Scope context for multi-tenancy support.

Provides the current user's scope (team or campaign) for request-scoped filtering.
Uses Python's contextvars for global request-scoped access.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Literal
from litestar import Request
from litestar.exceptions import NotAuthorizedException
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaigns.models import Campaign

# Global context variable for current request's scope
_current_scope: ContextVar[CurrentScope | None] = ContextVar(
    "current_scope", default=None
)


@dataclass
class CurrentScope:
    """Current user's scope context.

    Users can have either team scope OR campaign scope active at a time.
    - Team scope: Full access to all team resources
    - Campaign scope: Limited access to specific campaign resources
    """

    user_id: int
    scope_type: Literal["team", "campaign"]
    team_id: int | None = None  # Set if scope_type="team"
    campaign_id: int | None = None  # Set if scope_type="campaign"

    @property
    def is_team_scoped(self) -> bool:
        """Check if user has team scope."""
        return self.scope_type == "team"

    @property
    def is_campaign_scoped(self) -> bool:
        """Check if user has campaign scope."""
        return self.scope_type == "campaign"

    async def get_effective_team_id(self, session: AsyncSession) -> int:
        """Get the effective team_id for filtering.

        For team scope, returns team_id directly.
        For campaign scope, loads the campaign and returns its team_id.
        """
        if self.scope_type == "team":
            if self.team_id is None:
                raise ValueError("Team scope requires team_id")
            return self.team_id
        else:
            if self.campaign_id is None:
                raise ValueError("Campaign scope requires campaign_id")
            # Load campaign to get its team_id
            campaign = await session.get(Campaign, self.campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {self.campaign_id} not found")
            return campaign.team_id


async def get_current_scope(request: Request) -> CurrentScope:
    """Dependency provider for current user scope.

    Extracts scope information from the session and returns a CurrentScope object.

    Raises:
        NotAuthorizedException: If user is not authenticated or scope is not set.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise NotAuthorizedException("Authentication required")

    scope_type = request.session.get("scope_type")
    if not scope_type:
        raise NotAuthorizedException("Scope not set - please select a team or campaign")

    if scope_type == "team":
        team_id = request.session.get("team_id")
        if not team_id:
            raise NotAuthorizedException("Team scope requires team_id in session")
        return CurrentScope(
            user_id=user_id, scope_type="team", team_id=team_id, campaign_id=None
        )
    elif scope_type == "campaign":
        campaign_id = request.session.get("campaign_id")
        if not campaign_id:
            raise NotAuthorizedException(
                "Campaign scope requires campaign_id in session"
            )
        return CurrentScope(
            user_id=user_id,
            scope_type="campaign",
            team_id=None,
            campaign_id=campaign_id,
        )
    else:
        raise NotAuthorizedException(f"Invalid scope_type: {scope_type}")


async def get_current_scope_optional(request: Request) -> CurrentScope | None:
    """Optional scope provider - returns None if not authenticated.

    Use this for routes that support both authenticated and unauthenticated access.
    """
    try:
        return await get_current_scope(request)
    except NotAuthorizedException:
        return None


def set_request_scope(scope: CurrentScope | None) -> None:
    """Set the current request's scope in context.

    Called by middleware at the start of each request.
    """
    _current_scope.set(scope)


def get_request_scope() -> CurrentScope | None:
    """Get the current request's scope from context.

    Returns None if no scope is set (unauthenticated request).
    This is the primary way to access scope - no parameters needed!
    """
    return _current_scope.get()
