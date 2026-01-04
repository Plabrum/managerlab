from datetime import date, datetime
from decimal import Decimal

from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
from app.threads.schemas import ThreadUnreadInfo
from app.utils.sqids import Sqid


class InvoiceSchema(BaseSchema):
    """Manual schema for Invoice model."""

    id: Sqid
    invoice_number: int
    customer_name: str
    customer_email: str
    posting_date: date
    due_date: date
    amount_due: Decimal
    amount_paid: Decimal
    description: str | None
    notes: str | None
    state: str
    created_at: datetime
    updated_at: datetime
    campaign_id: int | None
    team_id: int | None
    actions: list[ActionDTO]
    thread: ThreadUnreadInfo | None = None


class InvoiceUpdateSchema(BaseSchema):
    """Declarative update schema for Invoice - all fields required."""

    invoice_number: int
    customer_name: str
    customer_email: str
    posting_date: date
    due_date: date
    amount_due: Decimal
    amount_paid: Decimal
    description: str | None
    notes: str | None
    campaign_id: int | None


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
