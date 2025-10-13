from enum import StrEnum, auto


class MediaStates(StrEnum):
    """Media processing states."""

    PENDING = auto()
    PROCESSING = auto()
    READY = auto()
    FAILED = auto()


class MediaActions(StrEnum):
    """Actions for Media objects."""

    download = "media.download"
    delete = "media.delete"
    update = "media.update"


class TopLevelMediaActions(StrEnum):
    """Top-level Media actions (no object context)."""

    create = "top_level_media.create"
