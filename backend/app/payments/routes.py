from litestar import Request, Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.payments.models import Invoice
from app.payments.schemas import InvoiceSchema, InvoiceUpdateSchema
from app.utils.sqids import Sqid
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model
from app.actions.registry import ActionRegistry
from app.actions.enums import ActionGroupType
from app.threads.models import Thread

# Register InvoiceObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.payments.objects import InvoiceObject

ObjectRegistry().register(ObjectTypes.Invoices, InvoiceObject)


@get("/{id:str}")
async def get_invoice(
    id: Sqid,
    request: Request,
    transaction: AsyncSession,
    action_registry: ActionRegistry,
) -> InvoiceSchema:
    """Get an invoice by SQID."""
    from sqlalchemy.orm import joinedload, selectinload

    invoice = await get_or_404(
        transaction,
        Invoice,
        id,
        load_options=[
            joinedload(Invoice.thread).options(
                selectinload(Thread.messages),
                selectinload(Thread.read_statuses),
            )
        ],
    )

    # Compute actions for this invoice
    action_group = action_registry.get_class(ActionGroupType.InvoiceActions)
    actions = action_group.get_available_actions(obj=invoice)

    # Convert thread to unread info using the mixin method
    thread_info = invoice.get_thread_unread_info(request.user)

    return InvoiceSchema(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        customer_name=invoice.customer_name,
        customer_email=invoice.customer_email,
        posting_date=invoice.posting_date,
        due_date=invoice.due_date,
        amount_due=invoice.amount_due,
        amount_paid=invoice.amount_paid,
        description=invoice.description,
        notes=invoice.notes,
        state=invoice.state,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
        campaign_id=invoice.campaign_id,
        team_id=invoice.team_id,
        actions=actions,
        thread=thread_info,
    )


@post("/{id:str}")
async def update_invoice(
    id: Sqid, data: InvoiceUpdateSchema, request: Request, transaction: AsyncSession
) -> InvoiceSchema:
    """Update an invoice by SQID."""
    invoice = await get_or_404(transaction, Invoice, id)
    await update_model(
        session=transaction,
        model_instance=invoice,
        update_vals=data,
        user_id=request.user,
        team_id=invoice.team_id,
    )
    return InvoiceSchema(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        customer_name=invoice.customer_name,
        customer_email=invoice.customer_email,
        posting_date=invoice.posting_date,
        due_date=invoice.due_date,
        amount_due=invoice.amount_due,
        amount_paid=invoice.amount_paid,
        description=invoice.description,
        notes=invoice.notes,
        state=invoice.state,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
        campaign_id=invoice.campaign_id,
        team_id=invoice.team_id,
        actions=[],  # Update endpoints don't compute actions
    )


# Invoice router
invoice_router = Router(
    path="/invoices",
    guards=[requires_user_id],
    route_handlers=[
        get_invoice,
        update_invoice,
    ],
    tags=["invoices"],
)
