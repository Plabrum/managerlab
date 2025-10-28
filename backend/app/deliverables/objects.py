from app.campaigns.models import Campaign
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.actions.registry import ActionRegistry
from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    EnumFieldValue,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    StringFieldValue,
    DatetimeFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.deliverables.models import Deliverable, DeliverableMedia
from app.deliverables.enums import DeliverableStates, SocialMediaPlatforms
from app.utils.sqids import sqid_encode


class DeliverableObject(BaseObject):
    object_type = ObjectTypes.Deliverables
    model = Deliverable

    @classmethod
    def get_top_level_action_group(cls):
        return ActionGroupType.TopLevelDeliverableActions

    @classmethod
    def get_load_options(cls):
        """Return load options for eager loading relationships."""
        return [
            joinedload(Deliverable.deliverable_media_associations).options(
                selectinload(DeliverableMedia.media)
            ),
            joinedload(Deliverable.campaign).options(joinedload(Campaign.brand)),
            selectinload(Deliverable.media),
            selectinload(Deliverable.assigned_roster),
            joinedload(Deliverable.thread),
        ]

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
                    StringFieldValue(value=(deliverable.content))
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
