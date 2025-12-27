"""SavedView action enums."""

from enum import StrEnum, auto


class SavedViewActions(StrEnum):
    """Actions available for SavedView objects."""

    create = auto()
    update = auto()
    delete = auto()
    duplicate = auto()
    share = auto()  # Convert personal → team-shared
    unshare = auto()  # Convert team-shared → personal
