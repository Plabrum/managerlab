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
from app.posts.models import Post
from app.utils.sqids import sqid_encode


class PostObject(BaseObject):
    object_type = ObjectTypes.Post

    @classmethod
    def to_detail_dto(cls, post: Post) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="title",
                value=post.title,
                type=FieldType.String,
                label="Title",
                editable=True,
            ),
            ObjectFieldDTO(
                key="content",
                value=post.content,
                type=FieldType.Text,
                label="Content",
                editable=True,
            ),
            ObjectFieldDTO(
                key="platforms",
                value=post.platforms.value if post.platforms else None,
                type=FieldType.String,
                label="Platform",
                editable=True,
            ),
            ObjectFieldDTO(
                key="posting_date",
                value=post.posting_date.isoformat() if post.posting_date else None,
                type=FieldType.Datetime,
                label="Posting Date",
                editable=True,
            ),
            ObjectFieldDTO(
                key="compensation_structure",
                value=post.compensation_structure.value
                if post.compensation_structure
                else None,
                type=FieldType.String,
                label="Compensation Structure",
                editable=True,
            ),
            ObjectFieldDTO(
                key="notes",
                value=str(post.notes) if post.notes else "{}",
                type=FieldType.Text,
                label="Notes",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(post.id),
            object_type=ObjectTypes.Post,
            state=post.state.name,
            fields=fields,
            actions=[],
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, post: Post) -> ObjectListDTO:
        return ObjectListDTO(
            id=sqid_encode(post.id),
            object_type=ObjectTypes.Post,
            title=post.title,
            subtitle=post.content[:100] + "..."
            if post.content and len(post.content) > 100
            else post.content,
            state=post.state.name,
            actions=[],
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        query = select(Post)

        # Apply filters if provided
        if request.filters:
            if "title" in request.filters:
                query = query.where(Post.title.ilike(f"%{request.filters['title']}%"))
            if "content" in request.filters:
                query = query.where(
                    Post.content.ilike(f"%{request.filters['content']}%")
                )
            if "platforms" in request.filters:
                query = query.where(Post.platforms == request.filters["platforms"])
            if "search" in request.filters:
                search_term = f"%{request.filters['search']}%"
                query = query.where(
                    (Post.title.ilike(search_term)) | (Post.content.ilike(search_term))
                )

        # Apply sorting
        if request.sort_by:
            sort_column = getattr(Post, request.sort_by, None)
            if sort_column:
                if request.sort_order == "asc":
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
        else:
            # Default sort by posting_date desc
            query = query.order_by(Post.posting_date.desc())

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> Post:
        result = await session.get(Post, object_id)
        if not result:
            raise ValueError(f"Post with id {object_id} not found")
        return result

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[Post], int]:
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        posts = result.scalars().all()

        return posts, total
