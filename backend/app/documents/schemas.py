from datetime import datetime

from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
from app.client.s3_client import BaseS3Client
from app.documents.models import Document
from app.threads.schemas import ThreadUnreadInfo
from app.utils.sqids import Sqid


class DocumentSchema(BaseSchema):
    """Schema for Document model."""

    id: Sqid
    file_name: str
    file_type: str
    file_size: int
    mime_type: str
    state: str
    created_at: datetime
    updated_at: datetime
    team_id: int | None
    campaign_id: int | None


class DocumentResponseSchema(BaseSchema):
    """Standard document response schema with presigned URLs."""

    id: Sqid
    file_name: str
    file_type: str
    file_size: int
    mime_type: str
    state: str
    created_at: datetime
    updated_at: datetime
    download_url: str
    thumbnail_url: str | None
    actions: list[ActionDTO]
    thread: ThreadUnreadInfo | None = None


def document_to_response_schema(
    document: Document, s3_client: BaseS3Client, actions: list[ActionDTO], thread=None
) -> DocumentResponseSchema:
    """Transform Document model to response schema with presigned URLs.

    Args:
        document: Document model instance
        s3_client: S3Client for generating presigned URLs
        actions: List of available actions for this document
        thread: Optional thread unread info
    """
    download_url = s3_client.generate_presigned_download_url(key=document.file_key, expires_in=3600)
    thumbnail_url = (
        s3_client.generate_presigned_download_url(key=document.thumbnail_key, expires_in=3600)
        if document.thumbnail_key
        else None
    )

    return DocumentResponseSchema(
        id=document.id,  # Already a Sqid from the model
        file_name=document.file_name,
        file_type=document.file_type,
        file_size=document.file_size,
        mime_type=document.mime_type,
        state=document.state,
        created_at=document.created_at,
        updated_at=document.updated_at,
        download_url=download_url,
        thumbnail_url=thumbnail_url,
        actions=actions,
        thread=thread if thread is not None else document.thread,
    )


class DocumentUpdateSchema(BaseSchema):
    """Declarative update schema for Document - all fields required."""

    file_name: str


class PresignedUploadRequestSchema(BaseSchema):
    """Request schema for presigned upload URL."""

    file_name: str
    content_type: str
    file_size: int


class PresignedUploadResponseSchema(BaseSchema):
    """Response schema for presigned upload URL."""

    upload_url: str
    file_key: str


class RegisterDocumentSchema(BaseSchema):
    """Schema for registering an uploaded document file."""

    file_key: str
    file_name: str
    file_size: int
    mime_type: str
