from datetime import date, datetime

from msgspec import UNSET, UnsetType

from app.actions.schemas import ActionDTO
from app.addresses.schemas import AddressCreateSchema, AddressSchema
from app.base.schemas import BaseSchema
from app.threads.schemas import ThreadUnreadInfo
from app.utils.sqids import Sqid, sqid_decode


class RosterSchema(BaseSchema):
    """Schema for Roster model with all fields."""

    id: Sqid
    name: str
    email: str | None
    phone: str | None
    birthdate: date | None
    gender: str | None
    address: AddressSchema | None
    instagram_handle: str | None
    facebook_handle: str | None
    tiktok_handle: str | None
    youtube_channel: str | None
    profile_photo_id: int | None
    state: str
    created_at: datetime
    updated_at: datetime
    team_id: int | None
    actions: list[ActionDTO]
    thread: ThreadUnreadInfo | None = None


class RosterUpdateSchema(BaseSchema):
    """Schema for updating a roster member."""

    name: str | None | UnsetType = UNSET
    email: str | None | UnsetType = UNSET
    phone: str | None | UnsetType = UNSET
    birthdate: date | None | UnsetType = UNSET
    gender: str | None | UnsetType = UNSET
    address: AddressCreateSchema | None | UnsetType = UNSET
    instagram_handle: str | None | UnsetType = UNSET
    facebook_handle: str | None | UnsetType = UNSET
    tiktok_handle: str | None | UnsetType = UNSET
    youtube_channel: str | None | UnsetType = UNSET
    profile_photo_id: Sqid | None | UnsetType = UNSET


class RosterCreateSchema(BaseSchema):
    """Schema for creating a new roster member."""

    name: str
    email: str | None = None
    phone: str | None = None
    birthdate: date | None = None
    gender: str | None = None
    address: AddressCreateSchema | None = None
    instagram_handle: str | None = None
    facebook_handle: str | None = None
    tiktok_handle: str | None = None
    youtube_channel: str | None = None
    profile_photo_id: Sqid | None = None
