from datetime import date, datetime

from app.actions.schemas import ActionDTO
from app.addresses.schemas import AddressCreateSchema, AddressSchema
from app.base.schemas import BaseSchema
from app.threads.schemas import ThreadUnreadInfo
from app.utils.sqids import Sqid


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
    profile_photo_id: Sqid | None
    state: str
    created_at: datetime
    updated_at: datetime
    team_id: int | None
    actions: list[ActionDTO]
    thread: ThreadUnreadInfo | None = None


class RosterUpdateSchema(BaseSchema):
    """Schema for updating a roster member.

    Updates are declarative: the posted data represents the complete desired state.
    All fields are required. Use None to clear a field.
    """

    name: str
    email: str | None
    phone: str | None
    birthdate: date | None
    gender: str | None
    address: AddressCreateSchema | None
    instagram_handle: str | None
    facebook_handle: str | None
    tiktok_handle: str | None
    youtube_channel: str | None
    profile_photo_id: Sqid | None


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
