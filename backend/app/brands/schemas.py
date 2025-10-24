from datetime import datetime
from app.base.schemas import BaseSchema
from app.utils.sqids import Sqid
from app.actions.schemas import ActionDTO


class BrandSchema(BaseSchema):
    """Manual schema for Brand model."""

    id: Sqid
    name: str
    description: str | None
    website: str | None
    email: str | None
    phone: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    team_id: int | None
    actions: list[ActionDTO]


class BrandUpdateSchema(BaseSchema):
    """Schema for updating a Brand."""

    name: str | None = None
    description: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class BrandCreateSchema(BaseSchema):
    """Schema for creating a Brand."""

    name: str
    description: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class BrandContactSchema(BaseSchema):
    """Manual schema for BrandContact model."""

    id: Sqid
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    notes: str | None
    brand_id: int
    created_at: datetime
    updated_at: datetime
    team_id: int | None
    actions: list[ActionDTO] = []  # TODO: Implement BrandContactActions when needed


class BrandContactUpdateSchema(BaseSchema):
    """Schema for updating a BrandContact."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None
    brand_id: int | None = None


class BrandContactCreateSchema(BaseSchema):
    """Schema for creating a BrandContact."""

    first_name: str
    last_name: str
    brand_id: int
    email: str | None = None
    phone: str | None = None
    notes: str | None = None
