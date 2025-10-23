from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.payments.models import Invoice
from app.payments.schemas import InvoiceSchema, InvoiceUpdateSchema
from app.utils.sqids import Sqid
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model

# Register InvoiceObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.payments.objects import InvoiceObject

ObjectRegistry().register(ObjectTypes.Invoices, InvoiceObject)


@get("/{id:str}")
async def get_invoice(id: Sqid, transaction: AsyncSession) -> InvoiceSchema:
    """Get an invoice by SQID."""
    invoice = await get_or_404(transaction, Invoice, id)
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
    )


@post("/{id:str}")
async def update_invoice(
    id: Sqid, data: InvoiceUpdateSchema, transaction: AsyncSession
) -> InvoiceSchema:
    """Update an invoice by SQID."""
    invoice = await get_or_404(transaction, Invoice, id)
    update_model(invoice, data)
    await transaction.flush()
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
