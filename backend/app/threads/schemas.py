"""Thread schemas for request/response models."""

from datetime import datetime

from app.base.schemas import BaseSchema
from app.utils.sqids import Sqid


# Response schemas for models
class UserSchema(BaseSchema):
    """User information embedded in messages."""

    id: str  # public_id
    email: str
    name: str


class MessageSchema(BaseSchema):
    """Message response schema with user details."""

    id: str  # public_id
    thread_id: str  # thread public_id (sqid)
    user_id: str  # user public_id (sqid)
    content: str
    created_at: datetime
    updated_at: datetime
    user: UserSchema


# Request schemas
class MessageCreateSchema(BaseSchema):
    """Schema for creating a message."""

    content: str


class MessageUpdateSchema(BaseSchema):
    """Schema for updating a message."""

    content: str


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
