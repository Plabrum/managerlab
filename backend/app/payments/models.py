"""Invoice object model."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.objects.models.base import BaseObject
from app.objects.enums import InvoiceStates

if TYPE_CHECKING:
    pass


class Invoice(BaseObject):
    """Invoice object model."""

    __tablename__ = "invoices"
    _states_enum = InvoiceStates

    # Invoice-specific fields
    invoice_number: Mapped[int] = mapped_column(sa.Integer, nullable=False, unique=True)
    customer_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    customer_email: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    # Dates
    posting_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    due_date: Mapped[date] = mapped_column(sa.Date, nullable=False)

    # Amounts
    amount_due: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(
        sa.Numeric(10, 2), nullable=False, default=0
    )

    # Optional fields
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    def __init__(self, **kwargs):
        if "object_type" not in kwargs:
            kwargs["object_type"] = "invoice"
        if "state" not in kwargs:
            kwargs["state"] = InvoiceStates.DRAFT
        super().__init__(**kwargs)

    @property
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.amount_paid >= self.amount_due

    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        from datetime import date as date_module

        return (
            self.due_date < date_module.today()
            and not self.is_paid
            and self.state not in [InvoiceStates.CANCELLED, InvoiceStates.PAID]
        )

    @property
    def balance_due(self) -> Decimal:
        """Calculate remaining balance."""
        return self.amount_due - self.amount_paid
