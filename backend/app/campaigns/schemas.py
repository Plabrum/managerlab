from app.base.schemas import BaseSchema, SanitizedSQLAlchemyDTO
from app.campaigns.models import Campaign


class CampaignDTO(SanitizedSQLAlchemyDTO[Campaign]):
    """DTO for returning Campaign data."""

    pass


class CampaignUpdateSchema(BaseSchema):
    """Schema for updating a Campaign."""

    name: str | None = None
    description: str | None = None
    brand_id: int | None = None


class CampaignCreateSchema(BaseSchema):
    """Schema for creating a Campaign."""

    name: str
    brand_id: int
    description: str | None = None
