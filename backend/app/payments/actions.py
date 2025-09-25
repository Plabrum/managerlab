"""Invoice actions implementation."""

from typing import TYPE_CHECKING, Dict, Any
from decimal import Decimal

from app.actions.models import BaseAction
from app.objects.models.invoices import Invoice
from app.objects.enums import InvoiceStates
from app.objects.states.invoices import invoice_state_machine
from app.sm.services import StateMachineService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class MakeReadyAction(BaseAction):
    """Action to make invoice ready for sending."""

    action_name = "make_ready"
    label = "Mark as Ready"
    priority = 10

    async def is_available(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> bool:
        """Available when invoice is in draft state and has required fields."""
        return (
            obj.state == InvoiceStates.DRAFT.value
            and obj.invoice_number is not None
            and obj.customer_name
            and obj.customer_email
            and obj.amount_due > 0
        )

    async def perform(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Transition invoice to ready state."""
        machine_service = StateMachineService(invoice_state_machine)
        success = await machine_service.transition_to(
            session=session,
            obj=obj,
            target_state=InvoiceStates.READY,
            user_id=user_id,
            context=context,
        )

        return {
            "new_state": InvoiceStates.READY.value if success else None,
            "result": {"transitioned": success},
        }


class SendInvoiceAction(BaseAction):
    """Action to send invoice to customer."""

    action_name = "send_invoice"
    label = "Send Invoice"
    priority = 20

    async def is_available(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> bool:
        """Available when invoice is ready."""
        return obj.state == InvoiceStates.READY.value

    async def perform(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Send invoice and transition to sent state."""
        # Here you would integrate with email service
        # For now, just simulate sending

        machine_service = StateMachineService(invoice_state_machine)
        success = await machine_service.transition_to(
            session=session,
            obj=obj,
            target_state=InvoiceStates.SENT,
            user_id=user_id,
            context=context,
        )

        return {
            "new_state": InvoiceStates.SENT.value if success else None,
            "result": {
                "sent": success,
                "sent_to": obj.customer_email if success else None,
            },
        }


class RecordPaymentAction(BaseAction):
    """Action to record payment on invoice."""

    action_name = "record_payment"
    label = "Record Payment"
    priority = 30

    async def is_available(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> bool:
        """Available when invoice is sent or overdue and not fully paid."""
        return (
            obj.state in [InvoiceStates.SENT.value, InvoiceStates.OVERDUE.value]
            and not obj.is_paid
        )

    async def perform(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Record payment and potentially transition to paid."""
        if not context or "amount" not in context:
            return {"result": {"error": "Payment amount is required"}}

        try:
            payment_amount = Decimal(str(context["amount"]))
        except (ValueError, TypeError):
            return {"result": {"error": "Invalid payment amount"}}

        if payment_amount <= 0:
            return {"result": {"error": "Payment amount must be positive"}}

        # Record the payment
        old_amount_paid = obj.amount_paid
        obj.amount_paid += payment_amount

        # Don't allow overpayment
        if obj.amount_paid > obj.amount_due:
            obj.amount_paid = obj.amount_due

        actual_payment = obj.amount_paid - old_amount_paid

        # Check if invoice is now fully paid
        new_state = None
        if obj.is_paid:
            machine_service = StateMachineService(invoice_state_machine)
            success = await machine_service.transition_to(
                session=session,
                obj=obj,
                target_state=InvoiceStates.PAID,
                user_id=user_id,
                context=context,
            )
            new_state = InvoiceStates.PAID.value if success else None

        return {
            "new_state": new_state,
            "updated_fields": {"amount_paid": float(obj.amount_paid)},
            "result": {
                "payment_recorded": float(actual_payment),
                "new_balance": float(obj.balance_due),
                "fully_paid": obj.is_paid,
            },
        }


class SendReminderAction(BaseAction):
    """Action to send payment reminder."""

    action_name = "send_reminder"
    label = "Send Reminder"
    priority = 40

    async def is_available(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> bool:
        """Available when invoice is sent or overdue."""
        return obj.state in [
            InvoiceStates.SENT.value,
            InvoiceStates.OVERDUE.value,
        ]

    async def perform(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Send payment reminder."""
        # Here you would integrate with email service
        # For now, just simulate sending reminder

        return {
            "result": {
                "reminder_sent": True,
                "sent_to": obj.customer_email,
                "balance_due": float(obj.balance_due),
            }
        }


class GenerateBillLinkAction(BaseAction):
    """Action to generate payment link (only for managers)."""

    action_name = "generate_bill_link"
    label = "Generate Bill Link"
    priority = 50

    async def is_available(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> bool:
        """Available for managers when invoice is sent or overdue."""
        # This is where you'd check user permissions
        # For now, assume user_id 1 is a manager
        is_manager = user_id == 1  # Placeholder logic

        return is_manager and obj.state in [
            InvoiceStates.SENT.value,
            InvoiceStates.OVERDUE.value,
        ]

    async def perform(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Generate payment link."""
        # Here you would integrate with payment processor
        # For now, generate a mock link

        mock_link = f"https://pay.example.com/invoice/{obj.sqid}"

        return {
            "result": {"payment_link": mock_link, "amount_due": float(obj.balance_due)}
        }


class CancelInvoiceAction(BaseAction):
    """Action to cancel invoice."""

    action_name = "cancel_invoice"
    label = "Cancel Invoice"
    priority = 90

    async def is_available(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> bool:
        """Available when invoice is not paid or cancelled."""
        return obj.state != InvoiceStates.PAID.value

    async def perform(
        self,
        session: "AsyncSession",
        obj: Invoice,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Cancel invoice."""
        machine_service = StateMachineService(invoice_state_machine)
        success = await machine_service.transition_to(
            session=session,
            obj=obj,
            target_state=InvoiceStates.CANCELLED,
            user_id=user_id,
            context=context,
        )

        return {
            "new_state": InvoiceStates.CANCELLED.value if success else None,
            "result": {"cancelled": success},
        }
