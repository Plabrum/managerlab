"""Media object model."""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.objects.models.base import BaseObject
from app.objects.enums import MediaState

if TYPE_CHECKING:
    pass


class Media(BaseObject):
    """Media object model."""

    __tablename__ = "media"

    # Media-specific fields
    filename: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # File information
    file_size: Mapped[int | None] = mapped_column(
        sa.BigInteger, nullable=True
    )  # Size in bytes
    mime_type: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    file_extension: Mapped[str | None] = mapped_column(sa.String(20), nullable=True)

    # Media type and category
    media_type: Mapped[str | None] = mapped_column(
        sa.String(50), nullable=True
    )  # image, video, audio, document
    category: Mapped[str | None] = mapped_column(
        sa.String(100), nullable=True
    )  # logo, product, hero, etc.

    # URLs and storage
    url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    cdn_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    storage_provider: Mapped[str | None] = mapped_column(
        sa.String(50), nullable=True
    )  # s3, cloudinary, etc.

    # Image/Video specific
    width: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    duration: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True
    )  # Duration in seconds for video/audio
    aspect_ratio: Mapped[str | None] = mapped_column(
        sa.String(20), nullable=True
    )  # e.g., "16:9", "1:1"

    # Processing information
    processing_status: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    processing_progress: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True
    )  # 0-100
    processing_error: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Metadata
    exif_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    color_palette: Mapped[dict | None] = mapped_column(
        sa.JSON, nullable=True
    )  # Dominant colors
    alt_text: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    caption: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Usage tracking
    download_count: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, default=0
    )
    view_count: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, default=0)

    # Relations
    brand_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    campaign_id: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, index=True
    )
    uploader_user_id: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, index=True
    )

    # Copyright and licensing
    copyright_info: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    license_type: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    attribution: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)

    # Variants/versions
    variants: Mapped[dict | None] = mapped_column(
        sa.JSON, nullable=True
    )  # Different sizes/formats
    version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, default=1)
    parent_media_id: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, index=True
    )

    # Tags and organization
    tags: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    folder_path: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)

    # External service data
    external_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    external_service: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    external_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    def __init__(self, **kwargs):
        if "object_type" not in kwargs:
            kwargs["object_type"] = "media"
        if "state" not in kwargs:
            kwargs["state"] = MediaState.UPLOADING.value
        super().__init__(**kwargs)

    @property
    def is_image(self) -> bool:
        """Check if media is an image."""
        return self.media_type == "image"

    @property
    def is_video(self) -> bool:
        """Check if media is a video."""
        return self.media_type == "video"

    @property
    def is_ready(self) -> bool:
        """Check if media is ready for use."""
        return self.state == MediaState.READY.value

    @property
    def file_size_mb(self) -> float:
        """Get file size in MB."""
        if not self.file_size:
            return 0.0
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def display_name(self) -> str:
        """Get display name."""
        return self.title or self.original_filename or self.filename
