from datetime import date
from decimal import Decimal

from app.base.schemas import BaseSchema, SanitizedSQLAlchemyDTO
from app.payments.models import Invoice


class InvoiceDTO(SanitizedSQLAlchemyDTO[Invoice]):
    """DTO for returning Invoice data."""

    pass


class InvoiceUpdateSchema(BaseSchema):
    """Schema for updating an Invoice."""

    invoice_number: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    posting_date: date | None = None
    due_date: date | None = None
    amount_due: Decimal | None = None
    amount_paid: Decimal | None = None
    description: str | None = None
    notes: str | None = None
    campaign_id: int | None = None


class InvoiceCreateSchema(BaseSchema):
    """Schema for creating an Invoice."""

    invoice_number: int
    customer_name: str
    customer_email: str
    posting_date: date
    due_date: date
    amount_due: Decimal
    amount_paid: Decimal = Decimal("0")
    description: str | None = None
    notes: str | None = None
    campaign_id: int | None = None
