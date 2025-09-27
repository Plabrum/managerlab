from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.payments.models import Invoice
from app.base.schemas import SanitizedSQLAlchemyDTO, UpdateSQLAlchemyDTO
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_authenticated_user

# Register InvoiceObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.payments.object import InvoiceObject

ObjectRegistry.register(ObjectTypes.Invoice, InvoiceObject)


class InvoiceDTO(SanitizedSQLAlchemyDTO[Invoice]):
    """Data transfer object for Invoice model."""

    pass


class InvoiceUpdateDTO(UpdateSQLAlchemyDTO[Invoice]):
    """DTO for partial Invoice updates."""

    pass


@get("/{id:str}", return_dto=InvoiceDTO)
async def get_invoice(id: Sqid, transaction: AsyncSession) -> Invoice:
    """Get an invoice by SQID."""
    invoice_id = sqid_decode(id)
    invoice = await transaction.get(Invoice, invoice_id)
    if not invoice:
        raise ValueError(f"Invoice with id {id} not found")
    return invoice


@post("/{id:str}", return_dto=InvoiceDTO)
async def update_invoice(
    id: Sqid, data: InvoiceUpdateDTO, transaction: AsyncSession
) -> Invoice:
    """Update an invoice by SQID."""
    invoice_id = sqid_decode(id)
    invoice = await transaction.get(Invoice, invoice_id)
    if not invoice:
        raise ValueError(f"Invoice with id {id} not found")

    # Apply updates from DTO - partial=True means only provided fields are included
    for field, value in data.__dict__.items():
        if hasattr(invoice, field):  # Only update existing model fields
            setattr(invoice, field, value)

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
