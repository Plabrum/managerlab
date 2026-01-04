"""SavedView enums."""

from enum import StrEnum, auto


class DisplayMode(StrEnum):
    """Display mode for object list views."""

    TABLE = "table"
    GALLERY = "gallery"
    CARD = "card"
    LIST = "list"


class SavedViewActions(StrEnum):
    """Actions available for SavedView objects."""

    create = auto()
    update = auto()
    delete = auto()
    duplicate = auto()
    share = auto()  # Convert personal → team-shared
    unshare = auto()  # Convert team-shared → personal
