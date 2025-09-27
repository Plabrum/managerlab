from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.media.models import Media
from app.base.schemas import SanitizedSQLAlchemyDTO, UpdateSQLAlchemyDTO
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_authenticated_user

# Register MediaObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.media.object import MediaObject

ObjectRegistry.register(ObjectTypes.Media, MediaObject)


class MediaDTO(SanitizedSQLAlchemyDTO[Media]):
    """Data transfer object for Media model."""

    pass


class MediaUpdateDTO(UpdateSQLAlchemyDTO[Media]):
    """DTO for partial Media updates."""

    pass


@get("/{id:str}", return_dto=MediaDTO)
async def get_media(id: Sqid, transaction: AsyncSession) -> Media:
    """Get a media item by SQID."""
    media_id = sqid_decode(id)
    media = await transaction.get(Media, media_id)
    if not media:
        raise ValueError(f"Media with id {id} not found")
    return media


@post("/{id:str}", return_dto=MediaDTO)
async def update_media(
    id: Sqid, data: MediaUpdateDTO, transaction: AsyncSession
) -> Media:
    """Update a media item by SQID."""
    media_id = sqid_decode(id)
    media = await transaction.get(Media, media_id)
    if not media:
        raise ValueError(f"Media with id {id} not found")

    # Apply updates from DTO - partial=True means only provided fields are included
    for field, value in data.__dict__.items():
        if hasattr(media, field):  # Only update existing model fields
            setattr(media, field, value)

    await transaction.flush()
    return media


# Media router
media_router = Router(
    path="/media",
    guards=[requires_authenticated_user],
    route_handlers=[
        get_media,
        update_media,
    ],
    tags=["media"],
)
