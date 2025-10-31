"""Thread schemas for request/response models."""

from datetime import datetime
from typing import Any

from msgspec import Struct

from app.base.schemas import BaseSchema
from app.threads.enums import (
    ThreadSocketMessageType,
)
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


class ClientMessage(Struct, frozen=True):
    """Single unified client message structure.

    The message_type field determines which optional fields are relevant:
    - USER_FOCUS: No additional fields
    - USER_BLUR: No additional fields
    - MARK_READ: No additional fields
    """

    message_type: ThreadSocketMessageType


class ServerMessage(Struct, frozen=True):
    """Single unified server message structure.

    The type field determines which optional fields are relevant:
    - USER_JOINED: user_id, viewers
    - USER_LEFT: user_id, viewers
    - USER_FOCUS: user_id, viewers
    - USER_BLUR: user_id, viewers
    - MESSAGE_CREATED: message_id, thread_id, user_id, viewers
    - MESSAGE_UPDATED: message_id, thread_id, user_id, viewers
    - MESSAGE_DELETED: message_id, thread_id, user_id, viewers
    """

    message_type: ThreadSocketMessageType
    viewers: list[str]  # Always included - list of Sqid-encoded user IDs currently viewing
    user_id: str | None = None  # Sqid-encoded user ID
    message_id: str | None = None  # Sqid-encoded message ID
    thread_id: str | None = None  # Sqid-encoded thread ID
