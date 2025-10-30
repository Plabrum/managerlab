from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseAction, action_group_factory
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.payments.enums import InvoiceActions
from app.payments.models import Invoice
from app.payments.schemas import InvoiceUpdateSchema
from app.utils.db import update_model

invoice_actions = action_group_factory(ActionGroupType.InvoiceActions, model_type=Invoice)


@invoice_actions
class DeleteInvoice(BaseAction):
    action_key = InvoiceActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this invoice?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls,
        obj: Invoice,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted invoice",
        )


@invoice_actions
class UpdateInvoice(BaseAction):
    action_key = InvoiceActions.update
    label = "Update"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Invoice,
        data: InvoiceUpdateSchema,
        transaction: AsyncSession,
        user: int,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated invoice",
        )
