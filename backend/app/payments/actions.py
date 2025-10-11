from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.registry import action_group_factory
from app.actions.schemas import ActionExecutionResponse
from app.payments.enums import InvoiceActions
from app.payments.models import Invoice
from app.payments.routes import InvoiceUpdateDTO
from app.utils.dto import update_model


invoice_actions = action_group_factory(
    ActionGroupType.InvoiceActions, model_type=Invoice
)


@invoice_actions
class DeleteInvoice(BaseAction):
    action_key = InvoiceActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this invoice?"

    @classmethod
    async def execute(  # type: ignore[override]
        cls,
        obj: Invoice,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            success=True,
            message="Deleted invoice",
            results={},
        )


@invoice_actions
class UpdateInvoice(BaseAction):
    action_key = InvoiceActions.update
    label = "Update"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(  # type: ignore[override]
        cls,
        obj: Invoice,
        data: InvoiceUpdateDTO,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        update_model(obj, data)
        transaction.add(obj)

        return ActionExecutionResponse(
            success=True,
            message="Updated invoice",
            results={},
        )
