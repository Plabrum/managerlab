from app.base.schemas import BaseSchema, SanitizedSQLAlchemyDTO
from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact


class BrandDTO(SanitizedSQLAlchemyDTO[Brand]):
    """DTO for returning Brand data."""

    pass


class BrandUpdateSchema(BaseSchema):
    """Schema for updating a Brand."""

    name: str | None = None
    description: str | None = None
    tone_of_voice: str | None = None
    brand_values: str | None = None
    target_audience: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class BrandCreateSchema(BaseSchema):
    """Schema for creating a Brand."""

    name: str
    description: str | None = None
    tone_of_voice: str | None = None
    brand_values: str | None = None
    target_audience: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class BrandContactDTO(SanitizedSQLAlchemyDTO[BrandContact]):
    """DTO for returning BrandContact data."""

    pass


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
