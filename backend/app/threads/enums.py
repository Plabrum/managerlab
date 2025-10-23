"""Thread enums."""

from enum import StrEnum


class MessageActions(StrEnum):
    """Available actions for messages."""

    update = "update"
    delete = "delete"
