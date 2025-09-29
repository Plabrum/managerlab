from sqlalchemy.orm import selectinload
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_default_filters_for_field_type
from app.campaigns.models import Campaign
from app.utils.sqids import sqid_encode


class CampaignObject(BaseObject):
    object_type = ObjectTypes.Campaigns
    model = Campaign
    column_definitions = [
        ColumnDefinitionDTO(
            key="name",
            label="Name",
            type=FieldType.String,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="description",
            label="Description",
            type=FieldType.Text,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Text),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="brand",
            label="Brand",
            type=FieldType.URL,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Int),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created",
            type=FieldType.Datetime,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Datetime),
            default_visible=False,
        ),
        ColumnDefinitionDTO(
            key="state",
            label="Status",
            type=FieldType.Enum,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Enum),
            default_visible=False,
        ),
    ]

    @classmethod
    def get_load_options(cls):
        """Return load options for eager loading relationships."""
        return [selectinload(Campaign.brand)]

    @classmethod
    def to_detail_dto(cls, campaign: Campaign) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=campaign.name,
                type=FieldType.String,
                label="Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="description",
                value=campaign.description,
                type=FieldType.Text,
                label="Description",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(campaign.id),
            object_type=ObjectTypes.Campaigns,
            state="active",
            fields=fields,
            actions=[],
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, campaign: Campaign) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=campaign.name,
                type=FieldType.String,
                label="Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="description",
                value=campaign.description,
                type=FieldType.Text,
                label="Description",
                editable=False,
            ),
            ObjectFieldDTO(
                key="brand",
                value=campaign.brand.id,
                type=FieldType.URL,
                label=campaign.brand.name,
                editable=False,
            ),
            ObjectFieldDTO(
                key="state",
                value=campaign.state.value,
                type=FieldType.Enum,
                label="Status",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(campaign.id),
            object_type=ObjectTypes.Campaigns,
            title=campaign.name,
            subtitle=campaign.description,
            state="active",
            actions=[],
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            fields=fields,
        )
