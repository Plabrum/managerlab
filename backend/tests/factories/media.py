"""Media-related model factories."""

from datetime import UTC, datetime

from polyfactory import Use

from app.media.models import Media

from .base import BaseFactory


class MediaFactory(BaseFactory):
    """Factory for creating Media instances."""

    __model__ = Media

    filename = Use(BaseFactory.__faker__.file_name, extension="jpg")
    image_link = Use(BaseFactory.__faker__.image_url)
    thumnbnail_link = Use(BaseFactory.__faker__.image_url, width=200, height=200)
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-6m",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))
