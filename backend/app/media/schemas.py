from advanced_alchemy.extensions.litestar import SQLAlchemyDTOConfig
from app.base.schemas import (
    BaseSchema,
    SanitizedSQLAlchemyDTO,
)
from app.media.models import Media


class MediaDTO(SanitizedSQLAlchemyDTO[Media]):
    """Data transfer object for Media model."""

    config = SQLAlchemyDTOConfig(exclude={"file_key", "thumbnail_key", "deliverables"})


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
