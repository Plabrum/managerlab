"""Address schemas for validation and serialization."""

from datetime import datetime

from msgspec import UNSET, UnsetType

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
    """Schema for updating an address."""

    address1: str | None | UnsetType = UNSET
    address2: str | None | UnsetType = UNSET
    city: str | None | UnsetType = UNSET
    state: str | None | UnsetType = UNSET
    zip: str | None | UnsetType = UNSET
    country: str | None | UnsetType = UNSET
    address_type: AddressType | None | UnsetType = UNSET


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
