from enum import StrEnum, auto


class UserStates(StrEnum):
    NEEDS_TEAM = auto()
    ACTIVE = auto()
    DELETED = auto()
