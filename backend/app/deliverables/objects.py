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
    ObjectColumn,
)
from app.deliverables.models import Deliverable, DeliverableMedia
from app.deliverables.enums import DeliverableStates, SocialMediaPlatforms


class DeliverableObject(BaseObject):
    object_type = ObjectTypes.Deliverables
    model = Deliverable

    # Title/subtitle configuration
    title_field = "title"
    subtitle_field = "content_preview"
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

    column_definitions = [
        ObjectColumn(
            key="id",
            label="ID",
            type=FieldType.Int,
            value=lambda obj: obj.id,
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="content_preview",
            label="Content Preview",
            type=FieldType.String,
            value=lambda obj: (
                obj.content[:100] + "..."
                if obj.content and len(obj.content) > 100
                else obj.content
            ),
            sortable=False,
            default_visible=False,
            editable=False,
            nullable=True,
            include_in_list=False,
        ),
        ObjectColumn(
            key="created_at",
            label="Created At",
            type=FieldType.Datetime,
            value=lambda obj: obj.created_at,
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            value=lambda obj: obj.updated_at,
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="title",
            label="Title",
            type=FieldType.String,
            value=lambda obj: obj.title,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="content",
            label="Content",
            type=FieldType.String,
            value=lambda obj: obj.content,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="platforms",
            label="Platform",
            type=FieldType.Enum,
            value=lambda obj: obj.platforms,
            sortable=True,
            default_visible=True,
            available_values=[platform.value for platform in SocialMediaPlatforms],
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="state",
            label="Status",
            type=FieldType.Enum,
            value=lambda obj: obj.state,
            sortable=True,
            default_visible=True,
            available_values=[state.value for state in DeliverableStates],
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="posting_date",
            label="Posting Date",
            type=FieldType.Datetime,
            value=lambda obj: obj.posting_date,
            sortable=True,
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
