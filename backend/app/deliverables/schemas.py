from datetime import datetime
from typing import Any

from app.base.schemas import BaseSchema, SanitizedSQLAlchemyDTO
from app.deliverables.enums import SocialMediaPlatforms
from app.deliverables.models import Deliverable


class DeliverableDTO(SanitizedSQLAlchemyDTO[Deliverable]):
    """DTO for returning Deliverable data."""

    pass


class DeliverableUpdateSchema(BaseSchema):
    """Schema for updating a Deliverable."""

    title: str | None = None
    content: str | None = None
    platforms: SocialMediaPlatforms | None = None
    posting_date: datetime | None = None
    notes: dict[str, Any] | None = None
    campaign_id: int | None = None


class DeliverableCreateSchema(BaseSchema):
    """Schema for creating a Deliverable."""

    title: str
    platforms: SocialMediaPlatforms
    posting_date: datetime
    content: str | None = None
    notes: dict[str, Any] | None = None
    campaign_id: int | None = None


class AddMediaToDeliverableSchema(BaseSchema):
    """Schema for adding media to a Deliverable."""

    media_ids: list[int]


class RemoveMediaFromDeliverableSchema(BaseSchema):
    """Schema for removing media from a Deliverable."""

    media_ids: list[int]
