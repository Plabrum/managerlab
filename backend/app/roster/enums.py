from enum import StrEnum, auto


class RosterStates(StrEnum):
    """States for roster members (talent/influencers)."""

    PROSPECT = auto()
    ACTIVE = auto()
    INACTIVE = auto()
    ARCHIVED = auto()


class TopLevelRosterActions(StrEnum):
    """Top-level Roster actions (no object context)."""

    create = "top_level_roster.create"


class RosterActions(StrEnum):
    """Roster actions."""

    delete = "roster.delete"
    update = "roster.update"
