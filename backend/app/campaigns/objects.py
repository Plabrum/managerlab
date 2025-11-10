from sqlalchemy.orm import joinedload, selectinload

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
    ObjectFieldValue,
    StringFieldValue,
)
from app.utils.sqids import sqid_encode


class CampaignObject(BaseObject[Campaign]):
    object_type = ObjectTypes.Campaigns

    @classmethod
    def model(cls) -> type[Campaign]:
        return Campaign

    # Action groups
    top_level_action_group = ActionGroupType.CampaignActions
    action_group = ActionGroupType.CampaignActions

    # Load options for eager loading relationships
    load_options = [
        joinedload(Campaign.brand),
        joinedload(Campaign.thread),
        selectinload(Campaign.contract_versions),
        joinedload(Campaign.contract),
    ]

    @classmethod
    def title_field(cls, obj: Campaign) -> str:
        return obj.name

    @classmethod
    def subtitle_field(cls, obj: Campaign) -> str:
        return obj.description or ""

    @classmethod
    def state_field(cls, obj: Campaign) -> str:
        return obj.state

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
            value=lambda obj: (StringFieldValue(value=obj.description) if obj.description else None),
            sortable=True,
            default_visible=False,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="brand_id",
            label="Brand",
            type=FieldType.Object,
            value=lambda campaign: (
                ObjectFieldValue(
                    value=sqid_encode(campaign.brand.id),
                    label=campaign.brand.name,
                    object_type=ObjectTypes.Brands,
                )
                if campaign.brand
                else None
            ),
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
            object_type=ObjectTypes.Brands,
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
            value=lambda obj: (
                EnumFieldValue(value=obj.compensation_structure) if obj.compensation_structure else None
            ),
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=False,  # Not shown in original to_list_dto
        ),
    ]
