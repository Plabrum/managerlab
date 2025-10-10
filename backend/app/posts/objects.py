from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.posts.models import Post
from app.utils.sqids import sqid_encode


class PostObject(BaseObject):
    object_type = ObjectTypes.Posts
    model = Post
    column_definitions = [
        ColumnDefinitionDTO(
            key="title",
            label="Title",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="content",
            label="Content",
            type=FieldType.Text,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Text),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="platforms",
            label="Platform",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="posting_date",
            label="Posting Date",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="compensation_structure",
            label="Compensation",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=False,
        ),
    ]

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
                value=(
                    post.compensation_structure.value
                    if post.compensation_structure
                    else None
                ),
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

        action_group = ActionRegistry().get_class(ActionGroupType.PostActions)
        actions = action_group.get_available_actions(obj=post)

        return ObjectDetailDTO(
            id=sqid_encode(post.id),
            object_type=ObjectTypes.Posts,
            state=post.state.name,
            title=post.title,
            fields=fields,
            actions=actions,
            created_at=post.created_at,
            updated_at=post.updated_at,
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, post: Post) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="title",
                value=post.title,
                type=FieldType.String,
                label="Title",
                editable=False,
            ),
            ObjectFieldDTO(
                key="content",
                value=(
                    post.content[:100] + "..."
                    if post.content and len(post.content) > 100
                    else post.content
                ),
                type=FieldType.Text,
                label="Content",
                editable=False,
            ),
            ObjectFieldDTO(
                key="platforms",
                value=post.platforms.value if post.platforms else None,
                type=FieldType.String,
                label="Platform",
                editable=False,
            ),
            ObjectFieldDTO(
                key="posting_date",
                value=post.posting_date.isoformat() if post.posting_date else None,
                type=FieldType.Datetime,
                label="Posting Date",
                editable=False,
            ),
        ]

        action_group = ActionRegistry().get_class(ActionGroupType.PostActions)
        actions = action_group.get_available_actions(obj=post)

        return ObjectListDTO(
            id=sqid_encode(post.id),
            object_type=ObjectTypes.Posts,
            title=post.title,
            subtitle=(
                post.content[:100] + "..."
                if post.content and len(post.content) > 100
                else post.content
            ),
            state=post.state.name,
            actions=actions,
            created_at=post.created_at,
            updated_at=post.updated_at,
            fields=fields,
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        """Override default sorting for Post."""

        query = select(cls.model)

        # Apply structured filters and sorts using helper method
        query = cls.apply_request_to_query(query, cls.model, request)

        # Custom default sort for posts
        if not request.sorts:
            query = query.order_by(Post.posting_date.desc())

        return query
