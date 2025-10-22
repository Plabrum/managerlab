from datetime import datetime
from advanced_alchemy.extensions.litestar import SQLAlchemyDTOConfig
from app.base.schemas import (
    BaseSchema,
    SanitizedSQLAlchemyDTO,
)
from app.media.models import Media
from app.utils.sqids import Sqid


class MediaDTO(SanitizedSQLAlchemyDTO[Media]):
    """Data transfer object for Media model."""

    config = SQLAlchemyDTOConfig(exclude={"file_key", "thumbnail_key", "deliverables"})


class MediaResponseSchema(BaseSchema):
    """Standard media response schema with presigned URLs."""

    id: Sqid
    file_name: str
    file_type: str
    file_size: int
    mime_type: str
    state: str
    created_at: datetime
    updated_at: datetime
    view_url: str
    thumbnail_url: str | None


def media_to_response(media: Media, s3_client) -> MediaResponseSchema:
    """Transform Media model to response schema with presigned URLs.

    Args:
        media: Media model instance
        s3_client: S3Client for generating presigned URLs
    """
    view_url = s3_client.generate_presigned_download_url(
        key=media.file_key, expires_in=3600
    )
    thumbnail_url = (
        s3_client.generate_presigned_download_url(
            key=media.thumbnail_key, expires_in=3600
        )
        if media.thumbnail_key
        else None
    )

    return MediaResponseSchema(
        id=media.public_id,
        file_name=media.file_name,
        file_type=media.file_type,
        file_size=media.file_size,
        mime_type=media.mime_type,
        state=media.state,
        created_at=media.created_at,
        updated_at=media.updated_at,
        view_url=view_url,
        thumbnail_url=thumbnail_url,
    )


class MediaUpdateSchema(BaseSchema):
    file_name: str | None = None


class MediaWithUrlsSchema(BaseSchema):
    """Media response with presigned URLs."""

    id: str
    file_name: str
    file_type: str
    file_size: int
    mime_type: str
    status: str
    created_at: str
    updated_at: str
    view_url: str
    thumbnail_url: str


class PresignedUploadRequestSchema(BaseSchema):
    """Request schema for presigned upload URL."""

    file_name: str
    content_type: str
    file_size: int


class PresignedUploadResponseSchema(BaseSchema):
    """Response schema for presigned upload URL."""

    upload_url: str
    file_key: str


class RegisterMediaSchema(BaseSchema):
    """Schema for registering an uploaded media file."""

    file_key: str
    file_name: str
    file_size: int
    mime_type: str
