"""Invoice object model."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import DualScopedMixin
from app.payments.enums import InvoiceStates
from app.state_machine.models import StateMachineMixin


if TYPE_CHECKING:
    from app.campaigns.models import Campaign


class Invoice(
    DualScopedMixin,
    StateMachineMixin(states=InvoiceStates, initial_state=InvoiceStates.DRAFT),
    BaseDBModel,
):
    __tablename__ = "invoices"

    invoice_number: Mapped[int] = mapped_column(sa.Integer, nullable=False, unique=True)
    customer_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    customer_email: Mapped[str] = mapped_column(sa.Text, nullable=False)

    posting_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    due_date: Mapped[date] = mapped_column(sa.Date, nullable=False)

    amount_due: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(
        sa.Numeric(10, 2), nullable=False, default=0
    )

    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Relationships (campaign_id is from DualScopedMixin)
    campaign: Mapped["Campaign | None"] = relationship(
        "Campaign", back_populates="invoices"
    )
