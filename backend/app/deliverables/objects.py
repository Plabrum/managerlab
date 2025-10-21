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
from app.deliverables.models import Deliverable
from app.deliverables.enums import DeliverableStates, SocialMediaPlatforms
from app.utils.sqids import sqid_encode


class DeliverableObject(BaseObject):
    object_type = ObjectTypes.Deliverables
    model = Deliverable

    @classmethod
    def get_top_level_action_group(cls):
        return ActionGroupType.TopLevelDeliverableActions

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
            available_values=[state.value for state in DeliverableStates],
        ),
        ColumnDefinitionDTO(
            key="posting_date",
            label="Posting Date",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=True,
        ),
    ]

    @classmethod
    def to_detail_dto(cls, deliverable: Deliverable) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="title",
                value=StringFieldValue(value=deliverable.title),
                label="Title",
                editable=True,
            ),
            (
                ObjectFieldDTO(
                    key="content",
                    value=(
                        StringFieldValue(value=deliverable.content)
                        if deliverable.content
                        else None
                    ),
                    label="Content",
                    editable=True,
                )
            ),
            (
                ObjectFieldDTO(
                    key="platforms",
                    value=(
                        StringFieldValue(value=deliverable.platforms.value)
                        if deliverable.platforms
                        else None
                    ),
                    label="Platform",
                    editable=True,
                )
            ),
            (
                ObjectFieldDTO(
                    key="posting_date",
                    value=(
                        DatetimeFieldValue(value=deliverable.posting_date)
                        if deliverable.posting_date
                        else None
                    ),
                    label="Posting Date",
                    editable=True,
                )
            ),
            (
                ObjectFieldDTO(
                    key="notes",
                    value=(
                        TextFieldValue(value=deliverable.notes)
                        if deliverable.notes
                        else None
                    ),
                    label="Notes",
                    editable=True,
                )
            ),
        ]

        action_group = ActionRegistry().get_class(ActionGroupType.DeliverableActions)
        actions = action_group.get_available_actions(obj=deliverable)

        return ObjectDetailDTO(
            id=sqid_encode(deliverable.id),
            object_type=ObjectTypes.Deliverables,
            state=deliverable.state.name,
            title=deliverable.title,
            fields=fields,
            actions=actions,
            created_at=deliverable.created_at,
            updated_at=deliverable.updated_at,
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, deliverable: Deliverable) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="title",
                value=StringFieldValue(value=deliverable.title),
                label="Title",
                editable=False,
            ),
            ObjectFieldDTO(
                key="state",
                value=EnumFieldValue(value=deliverable.state.value),
                label="Status",
                editable=False,
            ),
            ObjectFieldDTO(
                key="content",
                value=(
                    TextFieldValue(
                        value=(
                            deliverable.content[:100] + "..."
                            if len(deliverable.content) > 100
                            else deliverable.content
                        )
                    )
                    if deliverable.content
                    else None
                ),
                label="Content",
                editable=False,
            ),
            ObjectFieldDTO(
                key="platforms",
                value=EnumFieldValue(value=deliverable.platforms.value),
                label="Platform",
                editable=False,
            ),
            ObjectFieldDTO(
                key="posting_date",
                value=(
                    DatetimeFieldValue(value=deliverable.posting_date)
                    if deliverable.posting_date
                    else None
                ),
                label="Posting Date",
                editable=False,
            ),
        ]

        action_group = ActionRegistry().get_class(ActionGroupType.DeliverableActions)
        actions = action_group.get_available_actions(obj=deliverable)

        return ObjectListDTO(
            id=sqid_encode(deliverable.id),
            object_type=ObjectTypes.Deliverables,
            title=deliverable.title,
            subtitle=(
                deliverable.content[:100] + "..."
                if deliverable.content and len(deliverable.content) > 100
                else deliverable.content
            ),
            state=deliverable.state.name,
            actions=actions,
            created_at=deliverable.created_at,
            updated_at=deliverable.updated_at,
            fields=fields,
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        """Override default sorting for Deliverable."""

        query = select(cls.model)

        # Apply structured filters and sorts using helper method
        query = cls.apply_request_to_query(query, cls.model, request)

        # Custom default sort for deliverables
        if not request.sorts:
            query = query.order_by(Deliverable.posting_date.desc())

        return query
