from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    StringFieldValue,
    IntFieldValue,
    TextFieldValue,
    EmailFieldValue,
    DateFieldValue,
    USDFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.payments.models import Invoice
from app.utils.sqids import sqid_encode


class InvoiceObject(BaseObject):
    object_type = ObjectTypes.Invoices
    model = Invoice
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
            key="invoice_number",
            label="Invoice #",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="customer_name",
            label="Customer",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="customer_email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Email),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="amount_due",
            label="Amount Due",
            type=FieldType.USD,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.USD),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="amount_paid",
            label="Amount Paid",
            type=FieldType.USD,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.USD),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="due_date",
            label="Due Date",
            type=FieldType.Date,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Date),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="posting_date",
            label="Posting Date",
            type=FieldType.Date,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Date),
            default_visible=False,
        ),
    ]

    @classmethod
    def to_detail_dto(cls, invoice: Invoice) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="invoice_number",
                value=IntFieldValue(value=invoice.invoice_number),
                label="Invoice Number",
                editable=False,
            ),
            ObjectFieldDTO(
                key="customer_name",
                value=StringFieldValue(value=invoice.customer_name),
                label="Customer Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="customer_email",
                value=EmailFieldValue(value=invoice.customer_email),
                label="Customer Email",
                editable=True,
            ),
            ObjectFieldDTO(
                key="posting_date",
                value=DateFieldValue(value=invoice.posting_date)
                if invoice.posting_date
                else None,
                label="Posting Date",
                editable=True,
            ),
            ObjectFieldDTO(
                key="due_date",
                value=DateFieldValue(value=invoice.due_date)
                if invoice.due_date
                else None,
                label="Due Date",
                editable=True,
            ),
            ObjectFieldDTO(
                key="amount_due",
                value=USDFieldValue(value=float(invoice.amount_due)),
                label="Amount Due",
                editable=True,
            ),
            ObjectFieldDTO(
                key="amount_paid",
                value=USDFieldValue(value=float(invoice.amount_paid)),
                label="Amount Paid",
                editable=True,
            ),
            ObjectFieldDTO(
                key="description",
                value=TextFieldValue(value=invoice.description)
                if invoice.description
                else None,
                label="Description",
                editable=True,
            ),
            ObjectFieldDTO(
                key="notes",
                value=TextFieldValue(value=invoice.notes) if invoice.notes else None,
                label="Notes",
                editable=True,
            ),
        ]

        action_group = ActionRegistry().get_class(ActionGroupType.InvoiceActions)
        actions = action_group.get_available_actions(obj=invoice)

        return ObjectDetailDTO(
            id=sqid_encode(invoice.id),
            object_type=ObjectTypes.Invoices,
            state=invoice.state.name,
            title=f"Invoice #{invoice.invoice_number}",
            fields=fields,
            actions=actions,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, invoice: Invoice) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="invoice_number",
                value=IntFieldValue(value=invoice.invoice_number),
                label="Invoice #",
                editable=False,
            ),
            ObjectFieldDTO(
                key="customer_name",
                value=StringFieldValue(value=invoice.customer_name),
                label="Customer",
                editable=False,
            ),
            ObjectFieldDTO(
                key="customer_email",
                value=EmailFieldValue(value=invoice.customer_email),
                label="Email",
                editable=False,
            ),
            ObjectFieldDTO(
                key="amount_due",
                value=USDFieldValue(value=float(invoice.amount_due)),
                label="Amount Due",
                editable=False,
            ),
            ObjectFieldDTO(
                key="amount_paid",
                value=USDFieldValue(value=float(invoice.amount_paid)),
                label="Amount Paid",
                editable=False,
            ),
            ObjectFieldDTO(
                key="due_date",
                value=DateFieldValue(value=invoice.due_date)
                if invoice.due_date
                else None,
                label="Due Date",
                editable=False,
            ),
        ]

        action_group = ActionRegistry().get_class(ActionGroupType.InvoiceActions)
        actions = action_group.get_available_actions(obj=invoice)

        return ObjectListDTO(
            id=sqid_encode(invoice.id),
            object_type=ObjectTypes.Invoices,
            title=f"Invoice #{invoice.invoice_number}",
            subtitle=f"{invoice.customer_name} - ${invoice.amount_due}",
            state=invoice.state.name,
            actions=actions,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
            fields=fields,
        )

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
