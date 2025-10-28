from sqlalchemy.orm import joinedload
from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.campaigns.models import Campaign
from app.campaigns.enums import CampaignStates
from app.utils.sqids import sqid_encode


class CampaignObject(BaseObject):
    object_type = ObjectTypes.Campaigns
    model = Campaign

    # Title/subtitle configuration
    title_field = "name"
    subtitle_field = "description"
    state_field = "state"

    # Action groups
    top_level_action_group = ActionGroupType.TopLevelCampaignActions
    action_group = ActionGroupType.CampaignActions

    # Load options for eager loading relationships
    load_options = [
        joinedload(Campaign.brand),
        joinedload(Campaign.thread),
    ]

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
            key="name",
            label="Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="description",
            label="Description",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=False,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="brand",
            label="Brand",
            type=FieldType.URL,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
            accessor=lambda campaign: f"brands/{sqid_encode(campaign.brand.id)}"
            if campaign.brand
            else None,
            formatter=lambda value: value,  # Already formatted by accessor
        ),
        ColumnDefinitionDTO(
            key="state",
            label="Status",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=False,
            available_values=[state.value for state in CampaignStates],
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="compensation_structure",
            label="Compensation",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=False,  # Not shown in original to_list_dto
        ),
    ]
