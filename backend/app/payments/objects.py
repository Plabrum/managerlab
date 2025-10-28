from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectListRequest,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.payments.models import Invoice


class InvoiceObject(BaseObject):
    object_type = ObjectTypes.Invoices
    model = Invoice

    # Title/subtitle configuration - will be customized in to_list_dto
    state_field = "state"

    # Action groups
    action_group = ActionGroupType.InvoiceActions

    @classmethod
    def to_list_dto(cls, obj: Invoice):
        dto = super().to_list_dto(obj)
        # Custom title and subtitle
        dto.title = f"Invoice #{obj.invoice_number}"
        dto.subtitle = f"{obj.customer_name} - ${obj.amount_due}"
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
            key="invoice_number",
            label="Invoice #",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="customer_name",
            label="Customer",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="customer_email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Email),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="amount_due",
            label="Amount Due",
            type=FieldType.USD,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.USD),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="amount_paid",
            label="Amount Paid",
            type=FieldType.USD,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.USD),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="due_date",
            label="Due Date",
            type=FieldType.Date,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Date),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="posting_date",
            label="Posting Date",
            type=FieldType.Date,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Date),
            default_visible=False,
            editable=False,
            nullable=True,
            include_in_list=False,
        ),
    ]

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        """Override default sorting for Invoice."""

        query = select(cls.model)

        # Apply structured filters and sorts using helper method
        query = cls.apply_request_to_query(query, cls.model, request)

        # Custom default sort for invoices
        if not request.sorts:
            query = query.order_by(Invoice.due_date.desc())

        return query
