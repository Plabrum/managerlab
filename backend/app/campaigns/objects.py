from sqlalchemy.orm import joinedload

from app.actions.enums import ActionGroupType
from app.campaigns.enums import CampaignStates
from app.campaigns.models import Campaign
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    DatetimeFieldValue,
    EnumFieldValue,
    FieldType,
    IntFieldValue,
    ObjectColumn,
    StringFieldValue,
    URLFieldValue,
)
from app.utils.sqids import sqid_encode


class CampaignObject(BaseObject[Campaign]):
    object_type = ObjectTypes.Campaigns

    @classmethod
    def model(cls) -> type[Campaign]:
        return Campaign

    # Action groups
    top_level_action_group = ActionGroupType.TopLevelCampaignActions
    action_group = ActionGroupType.CampaignActions

    # Load options for eager loading relationships
    load_options = [
        joinedload(Campaign.brand),
        joinedload(Campaign.thread),
    ]

    @classmethod
    def title_field(cls, campaign: Campaign) -> str:
        return campaign.name

    @classmethod
    def subtitle_field(cls, campaign: Campaign) -> str:
        return campaign.description or ""

    @classmethod
    def state_field(cls, campaign: Campaign) -> str:
        return campaign.state

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
            key="name",
            label="Name",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.name),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="description",
            label="Description",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.description) if obj.description else None,
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
            value=lambda campaign: (
                URLFieldValue(
                    value=f"brands/{sqid_encode(campaign.brand.id)}",
                    label=campaign.brand.name,
                )
                if campaign.brand
                else None
            ),
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
            value=lambda obj: EnumFieldValue(value=obj.state),
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
            value=lambda obj: EnumFieldValue(value=obj.compensation_structure) if obj.compensation_structure else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=False,  # Not shown in original to_list_dto
        ),
    ]
