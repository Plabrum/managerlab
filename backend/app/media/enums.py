from enum import StrEnum, auto


class MediaStates(StrEnum):
    """Media processing states."""

    PENDING = auto()
    PROCESSING = auto()
    READY = auto()
    FAILED = auto()


class MediaActions(StrEnum):
    """Actions for Media objects."""

    register = "media.register"
    download = "media.download"
    delete = "media.delete"
    update = "media.update"
