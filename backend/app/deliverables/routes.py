from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.deliverables.models import Deliverable, DeliverableMedia
from app.deliverables.schemas import (
    DeliverableResponseSchema,
    DeliverableUpdateSchema,
    deliverable_to_response,
)
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model
from app.client.s3_client import S3Dep


@get("/{id:str}")
async def get_deliverable(
    id: Sqid, transaction: AsyncSession, s3_client: S3Dep
) -> DeliverableResponseSchema:
    """Get a deliverable by SQID with type-safe field access and relations."""
    deliverable_id = sqid_decode(id)

    # Load deliverable with all relations eagerly
    deliverable = await get_or_404(
        transaction,
        Deliverable,
        deliverable_id,
        load_options=[
            joinedload(Deliverable.deliverable_media_associations).options(
                selectinload(DeliverableMedia.media)
            ),
            joinedload(Deliverable.campaign),
            selectinload(Deliverable.assigned_roster),
        ],
    )
    return deliverable_to_response(deliverable, s3_client)


@post("/{id:str}")
async def update_deliverable(
    id: Sqid, data: DeliverableUpdateSchema, transaction: AsyncSession, s3_client: S3Dep
) -> DeliverableResponseSchema:
    """Update a deliverable by SQID."""
    deliverable_id = sqid_decode(id)
    deliverable = await get_or_404(
        transaction,
        Deliverable,
        deliverable_id,
        load_options=[
            joinedload(Deliverable.deliverable_media_associations).options(
                selectinload(DeliverableMedia.media)
            ),
            selectinload(Deliverable.assigned_roster),
        ],
    )
    update_model(deliverable, data)
    await transaction.flush()
    return deliverable_to_response(deliverable, s3_client)


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
