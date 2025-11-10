from enum import StrEnum, auto


class DocumentStates(StrEnum):
    """Document processing states."""

    PENDING = auto()
    PROCESSING = auto()
    READY = auto()
    FAILED = auto()


class DocumentActions(StrEnum):
    """Actions for Document objects."""

    register = "document.register"
    download = "document.download"
    delete = "document.delete"
    update = "document.update"
