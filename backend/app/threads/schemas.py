"""Thread schemas for request/response models."""

from datetime import datetime
from typing import Any

from msgspec import Struct

from app.base.schemas import BaseSchema
from app.threads.enums import MessageUpdateType
from app.utils.sqids import Sqid


# Response schemas for models
class MessageSenderSchema(BaseSchema):
    """User information embedded in messages."""

    id: Sqid
    email: str
    name: str


class MessageSchema(BaseSchema):
    """Message response schema with user details."""

    id: Sqid
    thread_id: Sqid
    user_id: Sqid
    content: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    user: MessageSenderSchema


# Request schemas
class MessageCreateSchema(BaseSchema):
    """Schema for creating a message."""

    content: dict[str, Any]


class MessageUpdateSchema(BaseSchema):
    """Schema for updating a message."""

    content: dict[str, Any]


# Additional response schemas
class MessageListResponse(BaseSchema):
    """Response schema for paginated message list."""

    messages: list[MessageSchema]
    offset: int
    limit: int


class BatchUnreadRequest(BaseSchema):
    """Request schema for batch unread count."""

    object_ids: list[Sqid]


class ThreadUnreadInfo(BaseSchema):
    """Unread info for a single thread."""

    thread_id: Sqid
    unread_count: int


class BatchUnreadResponse(BaseSchema):
    """Response schema for batch unread counts."""

    threads: list[ThreadUnreadInfo]
    total_unread: int


# WebSocket event schemas
class UserPresence(BaseSchema):
    """User presence info for websocket events."""

    user_id: Sqid
    name: str
    is_typing: bool


# ============================================================================
# Websocket Message Schemas
# ============================================================================

# ============================================================================
# Client → Server Messages
# ============================================================================


class TypingMessage(Struct, frozen=True, tag="typing"):
    """Client typing indicator update."""

    is_typing: bool


class MarkReadMessage(Struct, frozen=True, tag="mark_read"):
    """Client request to mark thread as read."""

    pass


# Union of all client message types
ClientMessage = TypingMessage | MarkReadMessage


# ============================================================================
# Server → Client Messages
# ============================================================================


class UserJoinedMessage(Struct, frozen=True, tag="user_joined"):
    """Server notification that a user joined the thread."""

    user_id: str
    viewers: list[str]


class UserLeftMessage(Struct, frozen=True, tag="user_left"):
    """Server notification that a user left the thread."""

    user_id: str
    viewers: list[str]


class TypingUpdateMessage(Struct, frozen=True, tag="typing_update"):
    """Server notification that a user's typing status changed (transient)."""

    user_id: str
    is_typing: bool
    viewers: list[str]


class MessageUpdateMessage(Struct, frozen=True, tag="message_update"):
    """Server notification that a message was created, updated, or deleted."""

    update_type: MessageUpdateType
    message_id: str
    thread_id: str
    user_id: str
    viewers: list[int] = []  # Default empty, list of user IDs currently viewing


# Union of all server message types
ServerMessage = (
    UserJoinedMessage | UserLeftMessage | TypingUpdateMessage | MessageUpdateMessage
)
