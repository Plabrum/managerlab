from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    EnumFieldValue,
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    StringFieldValue,
    TextFieldValue,
    DatetimeFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.posts.models import Post
from app.posts.enums import PostStates, SocialMediaPlatforms
from app.utils.sqids import sqid_encode


class PostObject(BaseObject):
    object_type = ObjectTypes.Posts
    model = Post

    @classmethod
    def get_top_level_action_group(cls):
        return ActionGroupType.TopLevelPostActions

    column_definitions = [
        ColumnDefinitionDTO(
            key="id",
            label="ID",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=False,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
        ),
        ColumnDefinitionDTO(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
        ),
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
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            available_values=[platform.value for platform in SocialMediaPlatforms],
        ),
        ColumnDefinitionDTO(
            key="state",
            label="Status",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            available_values=[state.value for state in PostStates],
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
                value=StringFieldValue(value=post.title),
                label="Title",
                editable=True,
            ),
            ObjectFieldDTO(
                key="content",
                value=TextFieldValue(value=post.content) if post.content else None,
                label="Content",
                editable=True,
            ),
            ObjectFieldDTO(
                key="platforms",
                value=(
                    StringFieldValue(value=post.platforms.value)
                    if post.platforms
                    else None
                ),
                label="Platform",
                editable=True,
            ),
            ObjectFieldDTO(
                key="posting_date",
                value=(
                    DatetimeFieldValue(value=post.posting_date)
                    if post.posting_date
                    else None
                ),
                label="Posting Date",
                editable=True,
            ),
            ObjectFieldDTO(
                key="compensation_structure",
                value=(
                    StringFieldValue(value=post.compensation_structure.value)
                    if post.compensation_structure
                    else None
                ),
                label="Compensation Structure",
                editable=True,
            ),
            ObjectFieldDTO(
                key="notes",
                value=TextFieldValue(value=str(post.notes) if post.notes else "{}"),
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
                value=StringFieldValue(value=post.title),
                label="Title",
                editable=False,
            ),
            ObjectFieldDTO(
                key="state",
                value=EnumFieldValue(value=post.state.value),
                label="Status",
                editable=False,
            ),
            ObjectFieldDTO(
                key="content",
                value=(
                    TextFieldValue(
                        value=(
                            post.content[:100] + "..."
                            if len(post.content) > 100
                            else post.content
                        )
                    )
                    if post.content
                    else None
                ),
                label="Content",
                editable=False,
            ),
            ObjectFieldDTO(
                key="platforms",
                value=EnumFieldValue(value=post.platforms.value),
                label="Platform",
                editable=False,
            ),
            ObjectFieldDTO(
                key="posting_date",
                value=(
                    DatetimeFieldValue(value=post.posting_date)
                    if post.posting_date
                    else None
                ),
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
