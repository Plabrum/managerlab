from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import BaseObjectAction, BaseTopLevelAction, action_group_factory
from app.actions.base import EmptyActionData
from app.actions.deps import ActionDeps
from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.actions.state_actions import BaseUpdateStateAction
from app.payments.enums import InvoiceActions, InvoiceStates
from app.payments.models import Invoice
from app.payments.schemas import InvoiceCreateSchema, InvoiceUpdateSchema
from app.utils.db import create_model, update_model

invoice_actions = action_group_factory(ActionGroupType.InvoiceActions, model_type=Invoice)


@invoice_actions
class DeleteInvoice(BaseObjectAction[Invoice, EmptyActionData]):
    action_key = InvoiceActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this invoice?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls, obj: Invoice, data: EmptyActionData, transaction: AsyncSession, deps
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted invoice",
        )


@invoice_actions
class UpdateInvoice(BaseObjectAction[Invoice, InvoiceUpdateSchema]):
    action_key = InvoiceActions.update
    label = "Edit"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Invoice,
        data: InvoiceUpdateSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=deps.user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated invoice",
        )


@invoice_actions
class CreateInvoice(BaseTopLevelAction[InvoiceCreateSchema]):
    action_key = InvoiceActions.create
    label = "Create Invoice"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: InvoiceCreateSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        new_invoice = await create_model(
            session=transaction,
            team_id=deps.team_id,
            campaign_id=None,
            model_class=Invoice,
            create_vals=data,
            user_id=deps.user,
        )
        return ActionExecutionResponse(
            message=f"Created invoice #{new_invoice.invoice_number}",
        )


@invoice_actions
class UpdateInvoiceState(BaseUpdateStateAction[Invoice, InvoiceStates]):
    action_key = InvoiceActions.update_state
    state_enum = InvoiceStates
