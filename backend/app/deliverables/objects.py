from app.campaigns.models import Campaign
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectListRequest,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.deliverables.models import Deliverable, DeliverableMedia
from app.deliverables.enums import DeliverableStates, SocialMediaPlatforms


class DeliverableObject(BaseObject):
    object_type = ObjectTypes.Deliverables
    model = Deliverable

    # Title/subtitle configuration
    title_field = "title"
    state_field = "state"

    # Action groups
    top_level_action_group = ActionGroupType.TopLevelDeliverableActions
    action_group = ActionGroupType.DeliverableActions

    # Load options for eager loading relationships
    load_options = [
        joinedload(Deliverable.deliverable_media_associations).options(
            selectinload(DeliverableMedia.media)
        ),
        joinedload(Deliverable.campaign).options(joinedload(Campaign.brand)),
        selectinload(Deliverable.media),
        selectinload(Deliverable.assigned_roster),
        joinedload(Deliverable.thread),
    ]

    @classmethod
    def to_list_dto(cls, obj: Deliverable):
        dto = super().to_list_dto(obj)
        # Custom subtitle truncation
        if obj.content:
            dto.subtitle = (
                obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
            )
        return dto

    column_definitions = [
        ColumnDefinitionDTO(
            key="id",
            label="ID",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=False,
            include_in_list=False,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
            include_in_list=False,
        ),
        ColumnDefinitionDTO(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
            include_in_list=False,
        ),
        ColumnDefinitionDTO(
            key="title",
            label="Title",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="content",
            label="Content",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="platforms",
            label="Platform",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            available_values=[platform.value for platform in SocialMediaPlatforms],
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="state",
            label="Status",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            available_values=[state.value for state in DeliverableStates],
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="posting_date",
            label="Posting Date",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
    ]

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
