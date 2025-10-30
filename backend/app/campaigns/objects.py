from sqlalchemy.orm import joinedload
from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    FieldType,
    ObjectColumn,
)
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
            key="name",
            label="Name",
            type=FieldType.String,
            value=lambda obj: obj.name,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="description",
            label="Description",
            type=FieldType.String,
            value=lambda obj: obj.description,
            sortable=True,
            default_visible=False,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="brand",
            label="Brand",
            type=FieldType.URL,
            value=lambda campaign: f"brands/{sqid_encode(campaign.brand.id)}"
            if campaign.brand
            else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="state",
            label="Status",
            type=FieldType.Enum,
            value=lambda obj: obj.state,
            sortable=True,
            default_visible=False,
            available_values=[state.value for state in CampaignStates],
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="compensation_structure",
            label="Compensation",
            type=FieldType.Enum,
            value=lambda obj: obj.compensation_structure,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=False,  # Not shown in original to_list_dto
        ),
    ]
