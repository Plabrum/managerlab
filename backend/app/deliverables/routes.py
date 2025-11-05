from litestar import Request, Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.auth.guards import requires_user_id
from app.client.s3_client import S3Dep
from app.deliverables.models import Deliverable, DeliverableMedia
from app.deliverables.schemas import (
    DeliverableResponseSchema,
    DeliverableUpdateSchema,
    deliverable_to_response,
)
from app.media.models import Media
from app.threads.models import Thread
from app.utils.db import get_or_404, update_model
from app.utils.sqids import Sqid


@get("/{id:str}")
async def get_deliverable(
    request: Request, id: Sqid, transaction: AsyncSession, s3_client: S3Dep
) -> DeliverableResponseSchema:
    """Get a deliverable by SQID with type-safe field access and relations."""
    # id is already decoded from SQID string to int by msgspec

    # Load deliverable with all relations eagerly
    deliverable = await get_or_404(
        transaction,
        Deliverable,
        id,
        load_options=[
            joinedload(Deliverable.deliverable_media_associations).options(
                selectinload(DeliverableMedia.media).options(joinedload(Media.thread)),
                joinedload(DeliverableMedia.thread),
            ),
            joinedload(Deliverable.campaign),
            selectinload(Deliverable.assigned_roster),
            joinedload(Deliverable.thread).options(
                selectinload(Thread.messages),
                selectinload(Thread.read_statuses),
            ),
        ],
    )
    action_group = ActionRegistry().get_class(ActionGroupType.DeliverableActions)
    actions = action_group.get_available_actions(obj=deliverable)
    thread_info = deliverable.get_thread_unread_info(request.user)
    return deliverable_to_response(
        deliverable=deliverable,
        s3_client=s3_client,
        actions=actions,
        thread_info=thread_info,
    )


@post("/{id:str}")
async def update_deliverable(
    id: Sqid,
    data: DeliverableUpdateSchema,
    request: Request,
    transaction: AsyncSession,
    s3_client: S3Dep,
) -> DeliverableResponseSchema:
    """Update a deliverable by SQID."""
    # id is already decoded from SQID string to int by msgspec
    deliverable = await get_or_404(
        transaction,
        Deliverable,
        id,
        load_options=[
            joinedload(Deliverable.deliverable_media_associations).options(
                selectinload(DeliverableMedia.media),
                joinedload(DeliverableMedia.thread),
            ),
            selectinload(Deliverable.assigned_roster),
            joinedload(Deliverable.thread).options(
                selectinload(Thread.messages),
                selectinload(Thread.read_statuses),
            ),
        ],
    )
    await update_model(
        session=transaction,
        model_instance=deliverable,
        update_vals=data,
        user_id=request.user,
        team_id=deliverable.team_id,
    )

    action_group = ActionRegistry().get_class(ActionGroupType.DeliverableActions)
    actions = action_group.get_available_actions(obj=deliverable)
    thread_info = deliverable.get_thread_unread_info(request.user)
    return deliverable_to_response(
        deliverable=deliverable,
        s3_client=s3_client,
        actions=actions,
        thread_info=thread_info,
    )


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
