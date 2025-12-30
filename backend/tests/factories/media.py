"""Media-related model factories."""

from datetime import UTC, datetime

from polyfactory import Use

from app.media.enums import MediaStates
from app.media.models import Media

from .base import BaseFactory


class MediaFactory(BaseFactory):
    """Factory for creating Media instances."""

    __model__ = Media

    file_key = Use(BaseFactory.__faker__.uuid4)
    file_name = Use(BaseFactory.__faker__.file_name, extension="jpg")
    file_type = Use(BaseFactory.__faker__.random_element, elements=["image", "video"])
    file_size = Use(BaseFactory.__faker__.random_int, min=1000, max=10000000)
    mime_type = Use(BaseFactory.__faker__.random_element, elements=["image/jpeg", "image/png", "video/mp4"])
    thumbnail_key = None  # Optional
    state = MediaStates.PENDING
    campaign_id = None  # Optional - can be team-scoped or campaign-scoped
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-6m",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))
    deleted_at = None
