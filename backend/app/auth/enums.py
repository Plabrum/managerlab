from enum import Enum


class ScopeType(str, Enum):
    """Scope type for user access control.

    Users can have either team scope OR campaign scope active at a time.
    - TEAM: Full access to all team resources
    - CAMPAIGN: Limited access to specific campaign resources
    """

    TEAM = "team"
    CAMPAIGN = "campaign"
