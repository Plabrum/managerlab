from enum import StrEnum, auto


class DocumentStates(StrEnum):
    """Document processing states."""

    PENDING = auto()
    PROCESSING = auto()
    READY = auto()
    FAILED = auto()


class DocumentActions(StrEnum):
    """Actions for Document objects."""

    download = "document.download"
    delete = "document.delete"
    update = "document.update"


class TopLevelDocumentActions(StrEnum):
    """Top-level Document actions (no object context)."""

    create = "top_level_document.create"
