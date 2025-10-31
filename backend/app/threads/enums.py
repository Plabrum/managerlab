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


class ThreadSocketMessageType(StrEnum):
    """Types of messages server sends to clients."""

    MARK_READ = "mark_read"  # User marked thread as read
    USER_JOINED = "user_joined"  # User joined thread
    USER_LEFT = "user_left"  # User left thread
    USER_FOCUS = "user_focus"  # User started typing
    USER_BLUR = "user_blur"  # User stopped typing
    MESSAGE_CREATED = "message_created"  # New message created
    MESSAGE_UPDATED = "message_updated"  # Message updated
    MESSAGE_DELETED = "message_deleted"  # Message deleted
