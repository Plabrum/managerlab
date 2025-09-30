"""Payment-related model factories."""

from datetime import datetime, timezone
from decimal import Decimal

from polyfactory import Use

from app.payments.models import Invoice
from app.payments.enums import InvoiceStates
from .base import BaseFactory


class InvoiceFactory(BaseFactory):
    """Factory for creating Invoice instances."""

    __model__ = Invoice

    invoice_number = Use(BaseFactory.__faker__.unique.random_int, min=1000, max=99999)
    customer_name = Use(BaseFactory.__faker__.company)
    customer_email = Use(BaseFactory.__faker__.company_email)
    posting_date = Use(
        BaseFactory.__faker__.date_between, start_date="-3m", end_date="today"
    )
    due_date = Use(
        BaseFactory.__faker__.date_between, start_date="today", end_date="+2m"
    )
    amount_due = Use(
        lambda: Decimal(str(BaseFactory.__faker__.random_number(digits=4) / 100))
    )
    amount_paid = Use(lambda: Decimal("0.00"))
    description = Use(BaseFactory.__faker__.text, max_nb_chars=300)
    notes = Use(BaseFactory.__faker__.text, max_nb_chars=150)
    state = InvoiceStates.DRAFT
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-3m",
        end_date="now",
        tzinfo=timezone.utc,
    )
    updated_at = Use(lambda: datetime.now(tz=timezone.utc))
