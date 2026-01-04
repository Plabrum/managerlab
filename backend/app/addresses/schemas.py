"""Address schemas for validation and serialization."""

from datetime import datetime

from app.addresses.enums import AddressType
from app.base.schemas import BaseSchema
from app.utils.sqids import Sqid


class AddressCreateSchema(BaseSchema):
    """Schema for creating a new address."""

    address1: str
    city: str
    country: str = "US"
    address2: str | None = None
    state: str | None = None
    zip: str | None = None
    address_type: AddressType | None = None


class AddressUpdateSchema(BaseSchema):
    """Declarative update schema for Address - all fields required."""

    address1: str
    address2: str | None
    city: str
    state: str | None
    zip: str | None
    country: str
    address_type: AddressType | None


class AddressSchema(BaseSchema):
    """Schema for address response."""

    id: Sqid
    address1: str
    address2: str | None
    city: str
    state: str | None
    zip: str | None
    country: str
    address_type: AddressType | None
    team_id: int | None
    created_at: datetime
    updated_at: datetime
