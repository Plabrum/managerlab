from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
)
from app.media.models import Media
from app.utils.sqids import sqid_encode


class MediaObject(BaseObject):
    object_type = ObjectTypes.Media

    @classmethod
    def to_detail_dto(cls, media: Media) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="filename",
                value=media.filename,
                type=FieldType.String,
                label="Filename",
                editable=True,
            ),
            ObjectFieldDTO(
                key="image_link",
                value=media.image_link,
                type=FieldType.URL,
                label="Image Link",
                editable=True,
            ),
            ObjectFieldDTO(
                key="thumnbnail_link",
                value=media.thumnbnail_link,
                type=FieldType.URL,
                label="Thumbnail Link",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(media.id),
            object_type=ObjectTypes.Media,
            state="active",
            fields=fields,
            actions=[],
            created_at=media.created_at.isoformat(),
            updated_at=media.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, media: Media) -> ObjectListDTO:
        return ObjectListDTO(
            id=sqid_encode(media.id),
            object_type=ObjectTypes.Media,
            title=media.filename,
            subtitle=media.image_link,
            state="active",
            actions=[],
            created_at=media.created_at.isoformat(),
            updated_at=media.updated_at.isoformat(),
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        query = select(Media)

        # Apply filters if provided
        if request.filters:
            if "filename" in request.filters:
                query = query.where(
                    Media.filename.ilike(f"%{request.filters['filename']}%")
                )
            if "search" in request.filters:
                search_term = f"%{request.filters['search']}%"
                query = query.where(
                    (Media.filename.ilike(search_term))
                    | (Media.image_link.ilike(search_term))
                )

        # Apply sorting
        if request.sort_by:
            sort_column = getattr(Media, request.sort_by, None)
            if sort_column:
                if request.sort_order == "asc":
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
        else:
            # Default sort by created_at desc
            query = query.order_by(Media.created_at.desc())

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> Media:
        result = await session.get(Media, object_id)
        if not result:
            raise ValueError(f"Media with id {object_id} not found")
        return result

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[Media], int]:
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        media_items = result.scalars().all()

        return media_items, total
