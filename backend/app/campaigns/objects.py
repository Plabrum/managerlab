from sqlalchemy.orm import joinedload
from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    StringFieldValue,
    TextFieldValue,
    URLFieldValue,
    EnumFieldValue,
)
from app.objects.services import get_filter_by_field_type
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
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="description",
            label="Description",
            type=FieldType.Text,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Text),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="brand",
            label="Brand",
            type=FieldType.URL,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
        ),
        ColumnDefinitionDTO(
            key="state",
            label="Status",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=False,
        ),
    ]

    @classmethod
    def get_load_options(cls):
        """Return load options for eager loading relationships."""
        return [joinedload(Campaign.brand)]

    @classmethod
    def to_detail_dto(cls, campaign: Campaign) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=StringFieldValue(value=campaign.name),
                label="Name",
                editable=True,
            ),
        ]

        if campaign.description:
            fields.append(
                ObjectFieldDTO(
                    key="description",
                    value=TextFieldValue(value=campaign.description),
                    label="Description",
                    editable=True,
                )
            )

        action_group = ActionRegistry().get_class(ActionGroupType.CampaignActions)
        actions = action_group.get_available_actions(obj=campaign)

        return ObjectDetailDTO(
            id=sqid_encode(campaign.id),
            object_type=ObjectTypes.Campaigns,
            state="active",
            title=campaign.name,
            fields=fields,
            actions=actions,
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
                value=StringFieldValue(value=campaign.name),
                label="Name",
                editable=False,
            ),
        ]

        if campaign.description:
            fields.append(
                ObjectFieldDTO(
                    key="description",
                    value=TextFieldValue(value=campaign.description),
                    label="Description",
                    editable=False,
                )
            )

        if campaign.brand:
            fields.append(
                ObjectFieldDTO(
                    key="brand",
                    value=URLFieldValue(
                        value=f"brands/{sqid_encode(campaign.brand.id)}"
                    ),
                    label=campaign.brand.name,
                    editable=False,
                )
            )

        fields.append(
            ObjectFieldDTO(
                key="state",
                value=EnumFieldValue(value=campaign.state.value),
                label="Status",
                editable=False,
            )
        )

        action_group = ActionRegistry().get_class(ActionGroupType.CampaignActions)
        actions = action_group.get_available_actions(obj=campaign)

        return ObjectListDTO(
            id=sqid_encode(campaign.id),
            object_type=ObjectTypes.Campaigns,
            title=campaign.name,
            subtitle=campaign.description,
            state="active",
            actions=actions,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            fields=fields,
        )
