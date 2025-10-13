from datetime import datetime
from typing import Any

from app.base.schemas import BaseSchema, SanitizedSQLAlchemyDTO
from app.posts.enums import CompensationStructure, SocialMediaPlatforms
from app.posts.models import Post


class PostDTO(SanitizedSQLAlchemyDTO[Post]):
    """DTO for returning Post data."""

    pass


class PostUpdateSchema(BaseSchema):
    """Schema for updating a Post."""

    title: str | None = None
    content: str | None = None
    platforms: SocialMediaPlatforms | None = None
    posting_date: datetime | None = None
    notes: dict[str, Any] | None = None
    compensation_structure: CompensationStructure | None = None
    campaign_id: int | None = None


class PostCreateSchema(BaseSchema):
    """Schema for creating a Post."""

    title: str
    platforms: SocialMediaPlatforms
    posting_date: datetime
    content: str | None = None
    notes: dict[str, Any] | None = None
    compensation_structure: CompensationStructure | None = None
    campaign_id: int | None = None
