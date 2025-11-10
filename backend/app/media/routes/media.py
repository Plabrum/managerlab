import uuid

from litestar import Request, Router, delete, get, post
from litestar_saq import TaskQueues
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.auth.guards import requires_session
from app.client.s3_client import S3Dep
from app.media.enums import MediaStates
from app.media.models import Media
from app.media.schemas import (
    MediaResponseSchema,
    MediaSchema,
    PresignedUploadRequestSchema,
    PresignedUploadResponseSchema,
    RegisterMediaSchema,
    media_to_response_schema,
)
from app.utils.db import get_or_404
from app.utils.sqids import Sqid


@post("/presigned-upload")
async def request_presigned_upload(
    data: PresignedUploadRequestSchema, s3_client: S3Dep
) -> PresignedUploadResponseSchema:
    """Generate a presigned URL for uploading a file."""
    from litestar.exceptions import ValidationException

    from app.utils.configure import config

    # Validate file size
    if data.file_size > config.MAX_UPLOAD_SIZE:
        file_size_mb = data.file_size / (1024 * 1024)
        max_size_mb = config.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise ValidationException(f"File size {file_size_mb:.1f}MB exceeds maximum allowed size of {max_size_mb:.0f}MB")

    # Generate unique file key
    file_key = f"media/{uuid.uuid4()}/{data.file_name}"

    # Generate presigned URL
    upload_url = s3_client.generate_presigned_upload_url(key=file_key, content_type=data.content_type, expires_in=300)

    return PresignedUploadResponseSchema(upload_url=upload_url, file_key=file_key)


@post("/register")
async def register_media(
    data: RegisterMediaSchema,
    transaction: AsyncSession,
    task_queues: TaskQueues,
    request: Request,
) -> MediaSchema:
    """Register an uploaded media file and trigger thumbnail generation."""
    # Determine file type from mime_type
    file_type = "image" if data.mime_type.startswith("image/") else "video"
    # Create media record
    media = Media(
        team_id=request.session.get("team_id"),
        campaign_id=request.session.get("campaign_id"),
        file_key=data.file_key,
        file_name=data.file_name,
        file_size=data.file_size,
        mime_type=data.mime_type,
        file_type=file_type,
        state=MediaStates.PENDING,
    )
    transaction.add(media)
    await transaction.flush()
    queue = task_queues.get("default")
    await queue.enqueue("generate_thumbnail", media_id=int(media.id))
    return MediaSchema(
        id=media.id,
        file_name=media.file_name,
        file_type=media.file_type,
        file_size=media.file_size,
        mime_type=media.mime_type,
        state=media.state,
        created_at=media.created_at,
        updated_at=media.updated_at,
        team_id=media.team_id,
        campaign_id=media.campaign_id,
    )


@get("/{id:str}")
async def get_media(
    id: Sqid,
    transaction: AsyncSession,
    s3_client: S3Dep,
    action_registry: ActionRegistry,
) -> MediaResponseSchema:
    """Get a media item by SQID."""
    from sqlalchemy.orm import joinedload

    media = await get_or_404(transaction, Media, id, load_options=[joinedload(Media.thread)])

    # Compute actions for this media
    action_group = action_registry.get_class(ActionGroupType.MediaActions)
    actions = action_group.get_available_actions(obj=media)

    return media_to_response_schema(media, s3_client, actions)


@delete("/{id:str}", status_code=200)
async def delete_media(id: Sqid, transaction: AsyncSession, s3_client: S3Dep) -> dict[str, str]:
    """Delete a media item and its files from S3."""
    # id is already decoded from SQID string to int by msgspec
    media = await transaction.get(Media, id)
    if not media:
        raise ValueError(f"Media with id {id} not found")

    # Delete files from S3
    s3_client.delete_file(media.file_key)
    if media.thumbnail_key:
        s3_client.delete_file(media.thumbnail_key)

    # Delete from database
    await transaction.delete(media)

    return {"status": "deleted"}


# Media router
media_router = Router(
    path="/media",
    guards=[requires_session],
    route_handlers=[
        request_presigned_upload,
        register_media,
        get_media,
        delete_media,
    ],
    tags=["media"],
)
