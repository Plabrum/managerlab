"""Background tasks for media processing."""

import tempfile
from pathlib import Path
from saq.types import Context
from PIL import Image
import subprocess

from app.queue.registry import task
from app.media.models import Media


@task
async def generate_thumbnail(ctx: Context, *, media_id: int) -> dict:
    """Generate thumbnail for uploaded media file."""
    # Get dependencies from SAQ context
    db_sessionmaker = ctx["db_sessionmaker"]
    s3_client = ctx["s3_client"]

    # Use session with automatic transaction management
    async with db_sessionmaker() as session:
        async with session.begin():
            # Get media record
            media = await session.get(Media, media_id)
            if not media:
                return {"status": "error", "message": f"Media {media_id} not found"}

            # Update status to processing
            media.status = "processing"

            try:
                # Create temp directory for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)

                    # Download original file
                    original_path = temp_path / media.file_name
                    s3_client.download(original_path, media.file_key)

                    # Generate thumbnail based on file type
                    thumbnail_path = temp_path / f"thumb_{media.file_name}"

                    if media.file_type == "image":
                        # Use Pillow for images
                        with Image.open(original_path) as img:
                            # Convert to RGB if necessary (handles RGBA, P modes, etc.)
                            if img.mode in ("RGBA", "P", "LA"):
                                img = img.convert("RGB")

                            # Generate thumbnail maintaining aspect ratio
                            img.thumbnail((300, 300), Image.Resampling.LANCZOS)

                            # Save as JPEG
                            thumbnail_filename = (
                                f"thumb_{Path(media.file_name).stem}.jpg"
                            )
                            thumbnail_path = temp_path / thumbnail_filename
                            img.save(thumbnail_path, "JPEG", quality=85)

                    elif media.file_type == "video":
                        # Use ffmpeg for videos
                        thumbnail_filename = f"thumb_{Path(media.file_name).stem}.jpg"
                        thumbnail_path = temp_path / thumbnail_filename

                        # Extract frame at 1 second and resize to 300x300
                        subprocess.run(
                            [
                                "ffmpeg",
                                "-i",
                                str(original_path),
                                "-ss",
                                "00:00:01.000",
                                "-vframes",
                                "1",
                                "-vf",
                                "scale=300:300:force_original_aspect_ratio=decrease",
                                str(thumbnail_path),
                            ],
                            check=True,
                            capture_output=True,
                        )

                    # Upload thumbnail to S3
                    thumbnail_key = f"media/{media.file_key.split('/')[1]}/thumb_{thumbnail_filename}"
                    s3_client.upload(thumbnail_path, thumbnail_key)

                    # Update media record with thumbnail key
                    media.thumbnail_key = thumbnail_key
                    media.status = "ready"

                return {
                    "status": "success",
                    "media_id": media_id,
                    "thumbnail_key": thumbnail_key,
                }

            except Exception as e:
                # Mark as failed if anything goes wrong
                media.status = "failed"
                return {
                    "status": "error",
                    "media_id": media_id,
                    "message": str(e),
                }
