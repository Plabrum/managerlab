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


class TeamActions(StrEnum):
    """Team actions."""

    delete = "team.delete"
