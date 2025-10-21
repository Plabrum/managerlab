from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.deliverables.models import Deliverable
from app.deliverables.schemas import DeliverableDTO, DeliverableUpdateSchema
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model


@get("/{id:str}", return_dto=DeliverableDTO)
async def get_deliverable(id: Sqid, transaction: AsyncSession) -> Deliverable:
    """Get a deliverable by SQID."""
    deliverable_id = sqid_decode(id)
    return await get_or_404(transaction, Deliverable, deliverable_id)


@post("/{id:str}", return_dto=DeliverableDTO)
async def update_deliverable(
    id: Sqid, data: DeliverableUpdateSchema, transaction: AsyncSession
) -> Deliverable:
    """Update a deliverable by SQID."""
    deliverable_id = sqid_decode(id)
    deliverable = await get_or_404(transaction, Deliverable, deliverable_id)
    update_model(deliverable, data)
    await transaction.flush()
    return deliverable


# Deliverable router
deliverable_router = Router(
    path="/deliverables",
    guards=[requires_user_id],
    route_handlers=[
        get_deliverable,
        update_deliverable,
    ],
    tags=["deliverables"],
)
