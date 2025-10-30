from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    DateFieldValue,
    DatetimeFieldValue,
    EmailFieldValue,
    FieldType,
    IntFieldValue,
    ObjectColumn,
    StringFieldValue,
    USDFieldValue,
)
from app.payments.models import Invoice


class InvoiceObject(BaseObject[Invoice]):
    object_type = ObjectTypes.Invoices

    @classmethod
    def model(cls) -> type[Invoice]:
        return Invoice

    @classmethod
    def title_field(cls, invoice: Invoice) -> str:
        return f"Invoice #{invoice.invoice_number}"

    @classmethod
    def subtitle_field(cls, invoice: Invoice) -> str:
        return f"{invoice.customer_name} - ${invoice.amount_due}"

    @classmethod
    def state_field(cls, invoice: Invoice) -> str:
        return invoice.state

    # Action groups
    action_group = ActionGroupType.InvoiceActions

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
            key="invoice_title",
            label="Invoice Title",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=f"Invoice #{obj.invoice_number}"),
            sortable=False,
            default_visible=False,
            editable=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="invoice_subtitle",
            label="Invoice Subtitle",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=f"{obj.customer_name} - ${obj.amount_due}"),
            sortable=False,
            default_visible=False,
            editable=False,
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
            key="invoice_number",
            label="Invoice #",
            type=FieldType.Int,
            value=lambda obj: IntFieldValue(value=obj.invoice_number),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="customer_name",
            label="Customer",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.customer_name),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="customer_email",
            label="Email",
            type=FieldType.Email,
            value=lambda obj: EmailFieldValue(value=obj.customer_email),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="amount_due",
            label="Amount Due",
            type=FieldType.USD,
            value=lambda obj: USDFieldValue(value=obj.amount_due),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="amount_paid",
            label="Amount Paid",
            type=FieldType.USD,
            value=lambda obj: USDFieldValue(value=obj.amount_paid),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="due_date",
            label="Due Date",
            type=FieldType.Date,
            value=lambda obj: DateFieldValue(value=obj.due_date) if obj.due_date else None,
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
            value=lambda obj: DateFieldValue(value=obj.posting_date) if obj.posting_date else None,
            sortable=True,
            default_visible=False,
            editable=False,
            nullable=True,
            include_in_list=False,
        ),
    ]
