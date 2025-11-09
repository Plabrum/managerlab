from enum import StrEnum, auto


class RosterStates(StrEnum):
    """States for roster members (talent/influencers)."""

    PROSPECT = auto()
    ACTIVE = auto()
    INACTIVE = auto()
    ARCHIVED = auto()


class RosterActions(StrEnum):
    """Roster actions."""

    create = "roster.create"
    delete = "roster.delete"
    update = "roster.update"
