"""Generic object routes and endpoints."""

from sqlalchemy.ext.asyncio import AsyncSession
from litestar import Response, Router, get, post, Request
from litestar.di import Provide

from app.objects.query import get_object_by_id, query_objects
from app.objects.services.base import ObjectService
from app.actions.services import ActionService
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListRequest,
    ObjectListResponse,
    PerformActionRequest,
)
from app.utils.sqids import Sqid


@get("/{object_type:str}/{id:str}")
async def get_object_detail(
    object_type: str,
    id: Sqid,
    request: Request,
    session: AsyncSession,
    object_service: ObjectService,
) -> ObjectDetailDTO:
    """Get detailed object information."""
    obj = await get_object_by_id(session, object_type, id)
    user_id = request.session.get("user_id")

    return await object_service.get_object_detail(
        session=session, obj=obj, user_id=user_id
    )


@post("/{object_type:str}")
async def list_objects(
    object_type: str,
    request: Request,
    data: ObjectListRequest,
    session: AsyncSession,
    object_service: ObjectService,
) -> ObjectListResponse:
    """List objects with filtering and pagination."""
    user_id = request.session.get("user_id")

    # Query objects using the query module
    objects, total = await query_objects(session, object_type, data)

    # Convert to DTOs
    object_dtos = []
    for obj in objects:
        dto = await object_service.get_object_list_item(
            session=session, obj=obj, user_id=user_id
        )
        object_dtos.append(dto)

    return ObjectListResponse(
        objects=object_dtos, total=total, limit=data.limit, offset=data.offset
    )


@post("/{object_type:str}/{id:str}/actions")
async def perform_object_action(
    object_type: str,
    id: Sqid,
    request: Request,
    data: PerformActionRequest,
    session: AsyncSession,
    action_service: ActionService,
) -> Response:
    """Perform an action on an object."""
    obj = await get_object_by_id(session, object_type, id)
    user_id = request.session.get("user_id")

    await action_service.perform_action(
        session=session,
        obj=obj,
        action_name=data.action,
        user_id=user_id,
        object_version=data.object_version,
        idempotency_key=data.idempotency_key,
        context=data.context,
    )
    return Response(content="Action completed", status_code=200)


def provide_object_service(action_service: ActionService) -> ObjectService:
    return ObjectService(action_service)


def provide_action_service() -> ActionService:
    return ActionService()


# Object router
object_router = Router(
    path="/o",
    route_handlers=[
        get_object_detail,
        list_objects,
        perform_object_action,
    ],
    dependencies={
        "object_service": Provide(provide_object_service, sync_to_thread=False),
        "action_service": Provide(provide_action_service, sync_to_thread=False),
    },
    tags=["objects"],
)
