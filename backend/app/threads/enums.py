"""Thread enums."""

from enum import StrEnum


class MessageActions(StrEnum):
    """Available actions for messages."""

    update = "update"
    delete = "delete"


class MessageUpdateType(StrEnum):
    """Type of message update."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
