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
    URLFieldValue,
    EnumFieldValue,
    DateFieldValue,
    IntFieldValue,
    FloatFieldValue,
    BoolFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.campaigns.models import Campaign
from app.campaigns.enums import CampaignStates
from app.utils.sqids import sqid_encode


class CampaignObject(BaseObject):
    object_type = ObjectTypes.Campaigns
    model = Campaign

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
            default_visible=False,
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
            sortable=False,
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
            available_values=[state.value for state in CampaignStates],
        ),
        ColumnDefinitionDTO(
            key="compensation_structure",
            label="Compensation",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
        ),
    ]

    @classmethod
    def get_top_level_action_group(cls):
        return ActionGroupType.TopLevelCampaignActions

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
            (
                ObjectFieldDTO(
                    key="description",
                    value=StringFieldValue(value=campaign.description),
                    label="Description",
                    editable=True,
                )
                if campaign.description
                else None
            ),
            # Counterparty
            (
                ObjectFieldDTO(
                    key="counterparty_type",
                    value=EnumFieldValue(value=campaign.counterparty_type.value),
                    label="Counterparty Type",
                    editable=True,
                )
                if campaign.counterparty_type
                else None
            ),
            (
                ObjectFieldDTO(
                    key="counterparty_name",
                    value=StringFieldValue(value=campaign.counterparty_name),
                    label="Counterparty Name",
                    editable=True,
                )
                if campaign.counterparty_name
                else None
            ),
            (
                ObjectFieldDTO(
                    key="counterparty_email",
                    value=StringFieldValue(value=campaign.counterparty_email),
                    label="Counterparty Email",
                    editable=True,
                )
                if campaign.counterparty_email
                else None
            ),
            # Compensation
            (
                ObjectFieldDTO(
                    key="compensation_structure",
                    value=EnumFieldValue(value=campaign.compensation_structure.value),
                    label="Compensation Structure",
                    editable=True,
                )
                if campaign.compensation_structure
                else None
            ),
            (
                ObjectFieldDTO(
                    key="compensation_total_usd",
                    value=FloatFieldValue(value=campaign.compensation_total_usd),
                    label="Total Compensation (USD)",
                    editable=True,
                )
                if campaign.compensation_total_usd
                else None
            ),
            (
                ObjectFieldDTO(
                    key="payment_terms_days",
                    value=IntFieldValue(value=campaign.payment_terms_days),
                    label="Payment Terms (Days)",
                    editable=True,
                )
                if campaign.payment_terms_days
                else None
            ),
            # Flight dates
            (
                ObjectFieldDTO(
                    key="flight_start_date",
                    value=DateFieldValue(value=campaign.flight_start_date),  # type: ignore
                    label="Flight Start Date",
                    editable=True,
                )
                if campaign.flight_start_date
                else None
            ),
            (
                ObjectFieldDTO(
                    key="flight_end_date",
                    value=DateFieldValue(value=campaign.flight_end_date),  # type: ignore
                    label="Flight End Date",
                    editable=True,
                )
                if campaign.flight_end_date
                else None
            ),
            # FTC & Usage
            (
                ObjectFieldDTO(
                    key="ftc_string",
                    value=StringFieldValue(value=campaign.ftc_string),
                    label="FTC Disclosure",
                    editable=True,
                )
                if campaign.ftc_string
                else None
            ),
            (
                ObjectFieldDTO(
                    key="usage_duration",
                    value=StringFieldValue(value=campaign.usage_duration),
                    label="Usage Duration",
                    editable=True,
                )
                if campaign.usage_duration
                else None
            ),
            (
                ObjectFieldDTO(
                    key="usage_territory",
                    value=StringFieldValue(value=campaign.usage_territory),
                    label="Usage Territory",
                    editable=True,
                )
                if campaign.usage_territory
                else None
            ),
            (
                ObjectFieldDTO(
                    key="usage_paid_media_option",
                    value=BoolFieldValue(value=campaign.usage_paid_media_option),
                    label="Paid Media Option",
                    editable=True,
                )
                if campaign.usage_paid_media_option is not None
                else None
            ),
            # Exclusivity
            (
                ObjectFieldDTO(
                    key="exclusivity_category",
                    value=StringFieldValue(value=campaign.exclusivity_category),
                    label="Exclusivity Category",
                    editable=True,
                )
                if campaign.exclusivity_category
                else None
            ),
            (
                ObjectFieldDTO(
                    key="exclusivity_days_before",
                    value=IntFieldValue(value=campaign.exclusivity_days_before),
                    label="Exclusivity Days Before",
                    editable=True,
                )
                if campaign.exclusivity_days_before
                else None
            ),
            (
                ObjectFieldDTO(
                    key="exclusivity_days_after",
                    value=IntFieldValue(value=campaign.exclusivity_days_after),
                    label="Exclusivity Days After",
                    editable=True,
                )
                if campaign.exclusivity_days_after
                else None
            ),
            # Ownership
            (
                ObjectFieldDTO(
                    key="ownership_mode",
                    value=EnumFieldValue(value=campaign.ownership_mode.value),
                    label="Ownership Mode",
                    editable=True,
                )
                if campaign.ownership_mode
                else None
            ),
            # Approval
            (
                ObjectFieldDTO(
                    key="approval_rounds",
                    value=IntFieldValue(value=campaign.approval_rounds),
                    label="Approval Rounds",
                    editable=True,
                )
                if campaign.approval_rounds
                else None
            ),
            (
                ObjectFieldDTO(
                    key="approval_sla_hours",
                    value=IntFieldValue(value=campaign.approval_sla_hours),
                    label="Approval SLA (Hours)",
                    editable=True,
                )
                if campaign.approval_sla_hours
                else None
            ),
        ]

        action_group = ActionRegistry().get_class(ActionGroupType.CampaignActions)
        actions = action_group.get_available_actions(obj=campaign)

        return ObjectDetailDTO(
            id=sqid_encode(campaign.id),
            object_type=ObjectTypes.Campaigns,
            state="active",
            title=campaign.name,
            fields=[f for f in fields if f is not None],
            actions=actions,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
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
                    value=StringFieldValue(value=campaign.description),
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
