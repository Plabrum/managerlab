from enum import StrEnum, auto


class UserStates(StrEnum):
    NEEDS_TEAM = auto()
    ACTIVE = auto()
    DELETED = auto()


class RoleLevel(StrEnum):
    """Role levels for team membership."""

    OWNER = auto()
    ADMIN = auto()
    MEMBER = auto()
    VIEWER = auto()


class RosterStates(StrEnum):
    """States for roster members (talent/influencers)."""

    PROSPECT = auto()
    ACTIVE = auto()
    INACTIVE = auto()
    ARCHIVED = auto()


class TopLevelRosterActions(StrEnum):
    """Top-level Roster actions (no object context)."""

    create = "top_level_roster.create"
