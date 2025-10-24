from datetime import datetime, date

from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
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


class RosterUpdateSchema(BaseSchema):
    """Schema for updating a roster member."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    birthdate: date | None = None
    instagram_handle: str | None = None
    facebook_handle: str | None = None
    tiktok_handle: str | None = None
    youtube_channel: str | None = None


class RosterCreateSchema(BaseSchema):
    """Schema for creating a new roster member."""

    name: str
    email: str | None = None
    phone: str | None = None
    instagram_handle: str | None = None
