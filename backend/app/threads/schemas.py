"""Thread schemas for request/response models."""

from datetime import datetime
from typing import Any

from app.base.schemas import BaseSchema
from app.utils.sqids import Sqid


# Response schemas for models
class UserSchema(BaseSchema):
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
    user: UserSchema


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
