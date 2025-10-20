"""Authentication schemas and DTOs."""

from msgspec import Struct

from app.auth.enums import ScopeType
from app.users.enums import RoleLevel
from app.campaigns.enums import CampaignGuestAccessLevel


class TeamScopeDTO(Struct):
    """Team scope information."""

    team_id: int
    team_name: str
    role_level: RoleLevel


class CampaignScopeDTO(Struct):
    """Campaign scope information."""

    campaign_id: int
    campaign_name: str
    team_id: int
    team_name: str
    access_level: CampaignGuestAccessLevel


class ListScopesResponse(Struct):
    """Response for listing available scopes."""

    teams: list[TeamScopeDTO]
    campaigns: list[CampaignScopeDTO]
    current_scope_type: str | None
    current_scope_id: int | None


class SwitchScopeRequest(Struct):
    """Request to switch scope."""

    scope_type: ScopeType
    scope_id: int  # team_id or campaign_id
