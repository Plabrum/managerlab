from datetime import date, datetime

from msgspec import UNSET, UnsetType

from app.actions.schemas import ActionDTO
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
    instagram_handle: str | None | UnsetType = UNSET
    facebook_handle: str | None | UnsetType = UNSET
    tiktok_handle: str | None | UnsetType = UNSET
    youtube_channel: str | None | UnsetType = UNSET


class RosterCreateSchema(BaseSchema):
    """Schema for creating a new roster member."""

    name: str
    email: str | None = None
    phone: str | None = None
    instagram_handle: str | None = None
