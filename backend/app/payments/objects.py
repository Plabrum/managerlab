from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectListRequest,
    FieldType,
    ObjectColumn,
)
from app.payments.models import Invoice


class InvoiceObject(BaseObject):
    object_type = ObjectTypes.Invoices
    model = Invoice

    # Title/subtitle configuration
    title_field = "invoice_title"
    subtitle_field = "invoice_subtitle"
    state_field = "state"

    # Action groups
    action_group = ActionGroupType.InvoiceActions

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
            key="invoice_title",
            label="Invoice Title",
            type=FieldType.String,
            value=lambda obj: f"Invoice #{obj.invoice_number}",
            sortable=False,
            default_visible=False,
            editable=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="invoice_subtitle",
            label="Invoice Subtitle",
            type=FieldType.String,
            value=lambda obj: f"{obj.customer_name} - ${obj.amount_due}",
            sortable=False,
            default_visible=False,
            editable=False,
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
            key="invoice_number",
            label="Invoice #",
            type=FieldType.Int,
            value=lambda obj: obj.invoice_number,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="customer_name",
            label="Customer",
            type=FieldType.String,
            value=lambda obj: obj.customer_name,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="customer_email",
            label="Email",
            type=FieldType.Email,
            value=lambda obj: obj.customer_email,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="amount_due",
            label="Amount Due",
            type=FieldType.USD,
            value=lambda obj: obj.amount_due,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="amount_paid",
            label="Amount Paid",
            type=FieldType.USD,
            value=lambda obj: obj.amount_paid,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="due_date",
            label="Due Date",
            type=FieldType.Date,
            value=lambda obj: obj.due_date,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="posting_date",
            label="Posting Date",
            type=FieldType.Date,
            value=lambda obj: obj.posting_date,
            sortable=True,
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
