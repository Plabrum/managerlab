from pathlib import Path
from io import BytesIO
from litestar import Router, get, put, Response, Request
from litestar.datastructures import ResponseHeader

from app.client.s3_client import S3Dep


# Local dev routes (no authentication for local file serving)
@put("/local-upload/{key:path}", guards=[])
async def local_upload(
    key: str,
    request: Request,
    s3_client: S3Dep,
) -> Response:
    """Handle local file uploads in development mode."""
    # Read raw body bytes
    data = await request.body()
    s3_client.upload_fileobj(BytesIO(data), key)
    return Response(content={"status": "uploaded"}, status_code=201)


@get("/local-download/{key:path}", guards=[])
async def local_download(key: str, s3_client: S3Dep) -> Response:
    """Serve local files in development mode."""

    if not s3_client.file_exists(key):
        raise ValueError(f"File not found: {key}")

    content = s3_client.get_file_bytes(key)

    # Determine content type from file extension
    suffix = Path(key).suffix.lower()
    content_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".avi": "video/x-msvideo",
        ".webm": "video/webm",
    }
    content_type = content_type_map.get(suffix, "application/octet-stream")

    return Response(
        content=content,
        media_type=content_type,
        headers=[
            ResponseHeader(name="Cache-Control", value="public, max-age=31536000"),
        ],
    )


local_media_router = Router(
    path="",
    guards=[],
    route_handlers=[local_upload, local_download],
    tags=["media-local"],
)
