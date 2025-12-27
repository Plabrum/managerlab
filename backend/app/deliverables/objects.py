from sqlalchemy.orm import joinedload, selectinload

from app.actions.enums import ActionGroupType
from app.campaigns.models import Campaign
from app.deliverables.enums import DeliverableStates, SocialMediaPlatforms
from app.deliverables.models import Deliverable, DeliverableMedia
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    DatetimeFieldValue,
    EnumFieldValue,
    FieldType,
    IntFieldValue,
    ObjectColumn,
    ObjectFieldValue,
    StringFieldValue,
)
from app.utils.sqids import sqid_encode


class DeliverableObject(BaseObject[Deliverable]):
    object_type = ObjectTypes.Deliverables

    @classmethod
    def model(cls) -> type[Deliverable]:
        return Deliverable

    @classmethod
    def title_field(cls, obj: Deliverable) -> str:
        return obj.title

    @classmethod
    def subtitle_field(cls, obj: Deliverable) -> str:
        content = obj.content
        if content and len(content) > 100:
            return content[:100] + "..."
        return content or ""

    @classmethod
    def state_field(cls, obj: Deliverable) -> str:
        return obj.state

    # Action groups
    top_level_action_group = ActionGroupType.DeliverableActions
    action_group = ActionGroupType.DeliverableActions

    # Load options for eager loading relationships
    load_options = [
        joinedload(Deliverable.deliverable_media_associations).options(selectinload(DeliverableMedia.media)),
        joinedload(Deliverable.campaign).options(
            joinedload(Campaign.brand),
            joinedload(Campaign.assigned_roster),
        ),
        selectinload(Deliverable.media),
        selectinload(Deliverable.assigned_roster),
        joinedload(Deliverable.thread),
    ]

    column_definitions = [
        ObjectColumn(
            key="id",
            label="ID",
            type=FieldType.Int,
            value=lambda obj: IntFieldValue(value=obj.id),
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="created_at",
            label="Created At",
            type=FieldType.Datetime,
            value=lambda obj: DatetimeFieldValue(value=obj.created_at),
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            value=lambda obj: DatetimeFieldValue(value=obj.updated_at),
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="title",
            label="Title",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.title),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="campaign_id",
            label="Campaign",
            type=FieldType.Object,
            value=lambda obj: (
                ObjectFieldValue(
                    value=sqid_encode(obj.campaign.id),
                    object_type=ObjectTypes.Campaigns,
                    label=obj.campaign.name,
                )
                if obj.campaign
                else None
            ),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
            object_type=ObjectTypes.Campaigns,
        ),
        ObjectColumn(
            key="content",
            label="Content",
            type=FieldType.String,
            value=lambda obj: (StringFieldValue(value=obj.content) if obj.content else None),
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
            value=lambda obj: EnumFieldValue(value=obj.platforms),
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
            value=lambda obj: EnumFieldValue(value=obj.state),
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
            value=lambda obj: (DatetimeFieldValue(value=obj.posting_date) if obj.posting_date else None),
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="owner_name",
            label="Owner Name",
            type=FieldType.String,
            value=lambda obj: (
                StringFieldValue(value=obj.campaign.assigned_roster.name)
                if obj.campaign and obj.campaign.assigned_roster and obj.campaign.assigned_roster.name
                else None
            ),
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
            query_relationship="assigned_roster",
            query_column="name",
        ),
        # ObjectColumn(
        #     key="content_owner",
        #     label="Content Owner",
        #     type=FieldType.Object,
        #     value=lambda obj: (
        #         ObjectFieldValue(
        #             value=sqid_encode(obj.content_owner.id),
        #             object_type=ObjectTypes.Roster,
        #             label=obj.content_owner.name,
        #         )
        #         if obj.content_owner
        #         else None
        #     ),
        #     sortable=True,
        #     default_visible=True,
        #     editable=False,
        #     nullable=True,
        #     include_in_list=True,
        #     object_type=ObjectTypes.Roster,
        # ),
    ]
