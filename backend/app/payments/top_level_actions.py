"""Top-level actions for invoices (actions that don't operate on specific invoice instances)."""

from litestar.dto import DTOData
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction, action_group_factory, ActionGroupType
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.payments.models import Invoice
from app.payments.enums import InvoiceActions


# Create invoice action group
top_level_invoice_actions = action_group_factory(ActionGroupType.TopLevelInvoiceActions)


@top_level_invoice_actions
class CreateInvoice(BaseAction):
    action_key = InvoiceActions.create
    label = "Create Invoice"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls, data: DTOData[Invoice], transaction: AsyncSession
    ) -> ActionExecutionResponse:
        new_invoice = data.create_instance()
        transaction.add(new_invoice)
        return ActionExecutionResponse(
            success=True,
            message=f"Created invoice #{new_invoice.invoice_number}",
            results={"invoice_id": new_invoice.id},
        )
