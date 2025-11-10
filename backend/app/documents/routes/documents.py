import uuid

from litestar import Request, Router, delete, get, post
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.auth.guards import requires_session
from app.client.s3_client import S3Dep
from app.documents.enums import DocumentStates
from app.documents.models import Document
from app.documents.schemas import (
    DocumentResponseSchema,
    DocumentSchema,
    PresignedUploadRequestSchema,
    PresignedUploadResponseSchema,
    RegisterDocumentSchema,
    document_to_response_schema,
)
from app.utils.db import get_or_404
from app.utils.sqids import Sqid


@post("/presigned-upload")
async def request_presigned_upload(
    data: PresignedUploadRequestSchema, s3_client: S3Dep
) -> PresignedUploadResponseSchema:
    """Generate a presigned URL for uploading a document file."""
    from litestar.exceptions import ValidationException

    from app.utils.configure import config

    # Validate file size against document limit (100MB)
    if data.file_size > config.MAX_DOCUMENT_SIZE:
        file_size_mb = data.file_size / (1024 * 1024)
        max_size_mb = config.MAX_DOCUMENT_SIZE / (1024 * 1024)
        raise ValidationException(f"File size {file_size_mb:.1f}MB exceeds maximum allowed size of {max_size_mb:.0f}MB")

    # Generate unique file key
    file_key = f"documents/{uuid.uuid4()}/{data.file_name}"

    # Generate presigned URL
    upload_url = s3_client.generate_presigned_upload_url(key=file_key, content_type=data.content_type, expires_in=300)

    return PresignedUploadResponseSchema(upload_url=upload_url, file_key=file_key)


@post("/register")
async def register_document(
    data: RegisterDocumentSchema,
    transaction: AsyncSession,
    request: Request,
) -> DocumentSchema:
    """Register an uploaded document file."""
    # Determine file type from mime_type or extension
    file_type = _determine_file_type(data.mime_type, data.file_name)

    # Create document record
    document = Document(
        team_id=request.session.get("team_id"),
        campaign_id=request.session.get("campaign_id"),
        file_key=data.file_key,
        file_name=data.file_name,
        file_size=data.file_size,
        mime_type=data.mime_type,
        file_type=file_type,
        state=DocumentStates.READY,  # No processing needed initially
    )
    transaction.add(document)
    await transaction.flush()

    return DocumentSchema(
        id=document.id,
        file_name=document.file_name,
        file_type=document.file_type,
        file_size=document.file_size,
        mime_type=document.mime_type,
        state=document.state,
        created_at=document.created_at,
        updated_at=document.updated_at,
        team_id=document.team_id,
        campaign_id=document.campaign_id,
    )


@get("/{id:str}")
async def get_document(
    id: Sqid,
    transaction: AsyncSession,
    s3_client: S3Dep,
    action_registry: ActionRegistry,
) -> DocumentResponseSchema:
    """Get a document item by SQID."""
    from sqlalchemy.orm import joinedload

    document = await get_or_404(transaction, Document, id, load_options=[joinedload(Document.thread)])

    # Compute actions for this document
    action_group = action_registry.get_class(ActionGroupType.DocumentActions)
    actions = action_group.get_available_actions(obj=document)

    return document_to_response_schema(document, s3_client, actions)


@delete("/{id:str}", status_code=200)
async def delete_document(id: Sqid, transaction: AsyncSession, s3_client: S3Dep) -> dict[str, str]:
    """Delete a document item and its file from S3."""
    document = await transaction.get(Document, id)
    if not document:
        raise ValueError(f"Document with id {id} not found")

    # Delete file from S3
    s3_client.delete_file(document.file_key)
    if document.thumbnail_key:
        s3_client.delete_file(document.thumbnail_key)

    # Delete from database
    await transaction.delete(document)

    return {"status": "deleted"}


@get("/")
async def list_documents(
    transaction: AsyncSession,
    s3_client: S3Dep,
    action_registry: ActionRegistry,
    request: Request,
) -> list[DocumentResponseSchema]:
    """List all documents for the current campaign."""
    campaign_id = request.session.get("campaign_id")

    # Build query
    query = select(Document)
    if campaign_id:
        query = query.where(Document.campaign_id == campaign_id)

    query = query.order_by(Document.created_at.desc())

    result = await transaction.execute(query)
    documents = result.scalars().all()

    # Compute actions for each document
    action_group = action_registry.get_class(ActionGroupType.DocumentActions)

    return [
        document_to_response_schema(
            document,
            s3_client,
            action_group.get_available_actions(obj=document),
        )
        for document in documents
    ]


def _determine_file_type(mime_type: str, file_name: str) -> str:
    """Determine document file type from MIME type or file extension.

    Returns a simple file type string like 'pdf', 'docx', 'xlsx', 'txt', etc.
    """
    # Map common MIME types to file types
    mime_type_map = {
        "application/pdf": "pdf",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/plain": "txt",
        "text/markdown": "md",
        "text/csv": "csv",
    }

    # Try MIME type first
    if mime_type in mime_type_map:
        return mime_type_map[mime_type]

    # Fallback to file extension
    if "." in file_name:
        extension = file_name.rsplit(".", 1)[-1].lower()
        return extension

    # Default fallback
    return "file"


# Document router
document_router = Router(
    path="/documents",
    guards=[requires_session],
    route_handlers=[
        request_presigned_upload,
        register_document,
        get_document,
        delete_document,
        list_documents,
    ],
    tags=["documents"],
)
