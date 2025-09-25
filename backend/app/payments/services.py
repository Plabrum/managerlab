"""Invoice service implementation."""

from typing import List


from app.objects.models.invoices import Invoice
from app.objects.enums import InvoiceStates
from app.objects.schemas import ObjectFieldDTO, FieldType
from app.objects.services.base import ObjectService


class InvoiceService(ObjectService):
    """Specialized service for invoice objects."""

    async def _get_object_fields(self, obj: Invoice) -> List[ObjectFieldDTO]:
        """Get invoice-specific fields."""
        fields = []

        # Basic info
        fields.append(
            ObjectFieldDTO(
                key="invoice_number",
                value=obj.invoice_number,
                type=FieldType.INT,
                label="Invoice Number",
                editable=False,
            )
        )

        # Customer info
        fields.append(
            ObjectFieldDTO(
                key="customer_name",
                value=obj.customer_name,
                type=FieldType.STRING,
                label="Customer Name",
            )
        )

        fields.append(
            ObjectFieldDTO(
                key="customer_email",
                value=obj.customer_email,
                type=FieldType.EMAIL,
                label="Customer Email",
            )
        )

        # Dates
        fields.append(
            ObjectFieldDTO(
                key="posting_date",
                value=obj.posting_date.isoformat(),
                type=FieldType.DATE,
                label="Posting Date",
            )
        )

        fields.append(
            ObjectFieldDTO(
                key="due_date",
                value=obj.due_date.isoformat(),
                type=FieldType.DATE,
                label="Due Date",
            )
        )

        # Amounts
        fields.append(
            ObjectFieldDTO(
                key="amount_due",
                value=float(obj.amount_due),
                type=FieldType.USD,
                label="Amount Due",
                editable=obj.state == InvoiceStates.DRAFT,
            )
        )

        fields.append(
            ObjectFieldDTO(
                key="amount_paid",
                value=float(obj.amount_paid),
                type=FieldType.USD,
                label="Amount Paid",
                editable=False,
            )
        )

        # Calculated fields
        fields.append(
            ObjectFieldDTO(
                key="balance_due",
                value=float(obj.balance_due),
                type=FieldType.USD,
                label="Balance Due",
                editable=False,
            )
        )

        # Optional fields
        if obj.description:
            fields.append(
                ObjectFieldDTO(
                    key="description",
                    value=obj.description,
                    type=FieldType.TEXT,
                    label="Description",
                )
            )

        if obj.notes:
            fields.append(
                ObjectFieldDTO(
                    key="notes", value=obj.notes, type=FieldType.TEXT, label="Notes"
                )
            )

        # Status indicators
        fields.append(
            ObjectFieldDTO(
                key="is_paid",
                value=obj.is_paid,
                type=FieldType.BOOL,
                label="Paid in Full",
                editable=False,
            )
        )

        fields.append(
            ObjectFieldDTO(
                key="is_overdue",
                value=obj.is_overdue,
                type=FieldType.BOOL,
                label="Overdue",
                editable=False,
            )
        )

        return fields

    async def _get_object_title_subtitle(self, obj: Invoice) -> tuple[str, str | None]:
        """Get title and subtitle for invoice."""
        title = f"Invoice {obj.invoice_number}"
        subtitle = f"{obj.customer_name} • ${obj.balance_due:,.2f}"
        return title, subtitle
