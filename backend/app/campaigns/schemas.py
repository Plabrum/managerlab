from datetime import datetime
from app.base.schemas import BaseSchema
from app.campaigns.enums import CompensationStructure
from app.utils.sqids import Sqid


class CampaignSchema(BaseSchema):
    """Manual schema for Campaign model."""

    id: Sqid
    name: str
    description: str | None
    compensation_structure: CompensationStructure | None
    assigned_roster_id: int | None
    brand_id: int
    state: str
    created_at: datetime
    updated_at: datetime
    team_id: int | None


class CampaignUpdateSchema(BaseSchema):
    """Schema for updating a Campaign."""

    name: str | None = None
    description: str | None = None
    brand_id: int | None = None
    compensation_structure: CompensationStructure | None = None


class CampaignCreateSchema(BaseSchema):
    """Schema for creating a Campaign."""

    name: str
    brand_id: Sqid
    description: str | None = None
    compensation_structure: CompensationStructure | None = None
