from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.payments.models import Invoice
from app.payments.schemas import InvoiceDTO, InvoiceUpdateSchema
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_authenticated_user
from app.utils.db import get_or_404, update_model

# Register InvoiceObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.payments.objects import InvoiceObject

ObjectRegistry().register(ObjectTypes.Invoices, InvoiceObject)


@get("/{id:str}", return_dto=InvoiceDTO)
async def get_invoice(id: Sqid, transaction: AsyncSession) -> Invoice:
    """Get an invoice by SQID."""
    invoice_id = sqid_decode(id)
    return await get_or_404(transaction, Invoice, invoice_id)


@post("/{id:str}", return_dto=InvoiceDTO)
async def update_invoice(
    id: Sqid, data: InvoiceUpdateSchema, transaction: AsyncSession
) -> Invoice:
    """Update an invoice by SQID."""
    invoice_id = sqid_decode(id)
    invoice = await get_or_404(transaction, Invoice, invoice_id)
    update_model(invoice, data)
    await transaction.flush()
    return invoice


# Invoice router
invoice_router = Router(
    path="/invoices",
    guards=[requires_authenticated_user],
    route_handlers=[
        get_invoice,
        update_invoice,
    ],
    tags=["invoices"],
)
