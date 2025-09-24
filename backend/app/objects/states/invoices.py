"""Invoice state machine implementation."""

from typing import TYPE_CHECKING, Dict, Any

from app.objects.models.sm import State, MachineSpec
from app.objects.models.invoices import Invoice
from app.objects.enums import InvoiceState

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class InvoiceDraftState(State[Invoice, InvoiceState]):
    """Draft state for invoices."""

    value = InvoiceState.DRAFT
    transitions = {InvoiceState.READY, InvoiceState.CANCELLED}

    async def can_leave(
        self,
        session: "AsyncSession",
        obj: Invoice,
        to: InvoiceState,
        ctx: Dict[str, Any] | None = None,
    ) -> bool:
        """Check if invoice can leave draft state."""
        if to == InvoiceState.READY:
            # Must have required fields filled
            return (
                obj.invoice_number is not None
                and obj.customer_name
                and obj.customer_email
                and obj.amount_due > 0
                and obj.posting_date is not None
                and obj.due_date is not None
            )
        return True  # Can always cancel


class InvoiceReadyState(State[Invoice, InvoiceState]):
    """Ready state for invoices."""

    value = InvoiceState.READY
    transitions = {InvoiceState.SENT, InvoiceState.DRAFT, InvoiceState.CANCELLED}


class InvoiceSentState(State[Invoice, InvoiceState]):
    """Sent state for invoices."""

    value = InvoiceState.SENT
    transitions = {InvoiceState.PAID, InvoiceState.OVERDUE, InvoiceState.CANCELLED}

    async def on_enter(
        self,
        session: "AsyncSession",
        obj: Invoice,
        from_state_class,
        ctx: Dict[str, Any] | None = None,
    ) -> None:
        """When invoice is sent, check if it should be overdue."""
        if obj.is_overdue:
            # Auto-transition to overdue if past due date
            from app.objects.services.sm import StateMachineService

            machine_service = StateMachineService(invoice_state_machine)
            await machine_service.transition_to(
                session=session,
                obj=obj,
                target_state=InvoiceState.OVERDUE,
                context={"auto_transition": "overdue_check"},
            )


class InvoicePaidState(State[Invoice, InvoiceState]):
    """Paid state for invoices."""

    value = InvoiceState.PAID
    transitions = {InvoiceState.SENT}  # Can revert if payment is reversed

    async def can_enter(
        self,
        session: "AsyncSession",
        obj: Invoice,
        from_state_class,
        ctx: Dict[str, Any] | None = None,
    ) -> bool:
        """Can only enter paid state if fully paid."""
        return obj.is_paid


class InvoiceOverdueState(State[Invoice, InvoiceState]):
    """Overdue state for invoices."""

    value = InvoiceState.OVERDUE
    transitions = {InvoiceState.PAID, InvoiceState.CANCELLED}

    async def can_enter(
        self,
        session: "AsyncSession",
        obj: Invoice,
        from_state_class,
        ctx: Dict[str, Any] | None = None,
    ) -> bool:
        """Can only enter overdue state if actually overdue."""
        return obj.is_overdue or ctx and ctx.get("auto_transition") == "overdue_check"


class InvoiceCancelledState(State[Invoice, InvoiceState]):
    """Cancelled state for invoices."""

    value = InvoiceState.CANCELLED
    transitions = set()  # Terminal state


# Define the invoice state machine
invoice_state_machine = MachineSpec[Invoice, InvoiceState](
    enum_type=InvoiceState,
    model_type=Invoice,
    initial=InvoiceState.DRAFT,
    name="invoice",
    states={
        InvoiceState.DRAFT: InvoiceDraftState,
        InvoiceState.READY: InvoiceReadyState,
        InvoiceState.SENT: InvoiceSentState,
        InvoiceState.PAID: InvoicePaidState,
        InvoiceState.OVERDUE: InvoiceOverdueState,
        InvoiceState.CANCELLED: InvoiceCancelledState,
    },
)
