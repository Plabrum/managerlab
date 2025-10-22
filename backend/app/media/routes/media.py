from litestar import Request, Router, post, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.media.enums import MediaStates
from app.media.models import Media
from app.media.schemas import (
    MediaDTO,
    PresignedUploadRequestSchema,
    PresignedUploadResponseSchema,
    RegisterMediaSchema,
)
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_user_id
from app.client.s3_client import S3Dep
from litestar_saq import TaskQueues


@post("/presigned-upload")
async def request_presigned_upload(
    data: PresignedUploadRequestSchema, s3_client: S3Dep
) -> PresignedUploadResponseSchema:
    """Generate a presigned URL for uploading a file."""
    from app.utils.configure import config
    from litestar.exceptions import ValidationException

    # Validate file size
    if data.file_size > config.MAX_UPLOAD_SIZE:
        raise ValidationException(
            f"File size {data.file_size / (1024*1024):.1f}MB exceeds maximum allowed size of {config.MAX_UPLOAD_SIZE / (1024*1024):.0f}MB"
        )

    # Generate unique file key
    file_key = f"media/{uuid.uuid4()}/{data.file_name}"

    # Generate presigned URL
    upload_url = s3_client.generate_presigned_upload_url(
        key=file_key, content_type=data.content_type, expires_in=300
    )

    return PresignedUploadResponseSchema(upload_url=upload_url, file_key=file_key)


@post("/register", return_dto=MediaDTO)
async def register_media(
    data: RegisterMediaSchema,
    transaction: AsyncSession,
    task_queues: TaskQueues,
    request: Request,
) -> Media:
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
    return media


@delete("/{id:str}", status_code=200)
async def delete_media(
    id: Sqid, transaction: AsyncSession, s3_client: S3Dep
) -> dict[str, str]:
    """Delete a media item and its files from S3."""
    media = await transaction.get(Media, sqid_decode(id))
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
    guards=[requires_user_id],
    route_handlers=[
        request_presigned_upload,
        register_media,
        delete_media,
    ],
    tags=["media"],
)
