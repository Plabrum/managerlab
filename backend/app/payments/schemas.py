from datetime import date, datetime
from decimal import Decimal

from msgspec import UNSET, UnsetType

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
    """Schema for updating an Invoice."""

    invoice_number: int | None | UnsetType = UNSET
    customer_name: str | None | UnsetType = UNSET
    customer_email: str | None | UnsetType = UNSET
    posting_date: date | None | UnsetType = UNSET
    due_date: date | None | UnsetType = UNSET
    amount_due: Decimal | None | UnsetType = UNSET
    amount_paid: Decimal | None | UnsetType = UNSET
    description: str | None | UnsetType = UNSET
    notes: str | None | UnsetType = UNSET
    campaign_id: int | None | UnsetType = UNSET


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
