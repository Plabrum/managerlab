from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.payments.models import Invoice
from app.utils.sqids import sqid_encode


class InvoiceObject(BaseObject):
    object_type = ObjectTypes.Invoices
    model = Invoice
    column_definitions = [
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
                value=invoice.invoice_number,
                type=FieldType.Int,
                label="Invoice Number",
                editable=False,
            ),
            ObjectFieldDTO(
                key="customer_name",
                value=invoice.customer_name,
                type=FieldType.String,
                label="Customer Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="customer_email",
                value=invoice.customer_email,
                type=FieldType.Email,
                label="Customer Email",
                editable=True,
            ),
            ObjectFieldDTO(
                key="posting_date",
                value=(
                    invoice.posting_date.isoformat() if invoice.posting_date else None
                ),
                type=FieldType.Date,
                label="Posting Date",
                editable=True,
            ),
            ObjectFieldDTO(
                key="due_date",
                value=invoice.due_date.isoformat() if invoice.due_date else None,
                type=FieldType.Date,
                label="Due Date",
                editable=True,
            ),
            ObjectFieldDTO(
                key="amount_due",
                value=float(invoice.amount_due),
                type=FieldType.USD,
                label="Amount Due",
                editable=True,
            ),
            ObjectFieldDTO(
                key="amount_paid",
                value=float(invoice.amount_paid),
                type=FieldType.USD,
                label="Amount Paid",
                editable=True,
            ),
            ObjectFieldDTO(
                key="description",
                value=invoice.description,
                type=FieldType.Text,
                label="Description",
                editable=True,
            ),
            ObjectFieldDTO(
                key="notes",
                value=invoice.notes,
                type=FieldType.Text,
                label="Notes",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(invoice.id),
            object_type=ObjectTypes.Invoices,
            state=invoice.state.name,
            title=f"Invoice #{invoice.invoice_number}",
            fields=fields,
            actions=[],
            created_at=invoice.created_at.isoformat(),
            updated_at=invoice.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, invoice: Invoice) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="invoice_number",
                value=invoice.invoice_number,
                type=FieldType.Int,
                label="Invoice #",
                editable=False,
            ),
            ObjectFieldDTO(
                key="customer_name",
                value=invoice.customer_name,
                type=FieldType.String,
                label="Customer",
                editable=False,
            ),
            ObjectFieldDTO(
                key="customer_email",
                value=invoice.customer_email,
                type=FieldType.Email,
                label="Email",
                editable=False,
            ),
            ObjectFieldDTO(
                key="amount_due",
                value=float(invoice.amount_due),
                type=FieldType.USD,
                label="Amount Due",
                editable=False,
            ),
            ObjectFieldDTO(
                key="amount_paid",
                value=float(invoice.amount_paid),
                type=FieldType.USD,
                label="Amount Paid",
                editable=False,
            ),
            ObjectFieldDTO(
                key="due_date",
                value=invoice.due_date.isoformat() if invoice.due_date else None,
                type=FieldType.Date,
                label="Due Date",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(invoice.id),
            object_type=ObjectTypes.Invoices,
            title=f"Invoice #{invoice.invoice_number}",
            subtitle=f"{invoice.customer_name} - ${invoice.amount_due}",
            state=invoice.state.name,
            actions=[],
            created_at=invoice.created_at.isoformat(),
            updated_at=invoice.updated_at.isoformat(),
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
