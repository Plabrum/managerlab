"""Generic object routes and endpoints."""

from sqlalchemy.ext.asyncio import AsyncSession
from litestar import Router, get, post, Request

from app.objects.base import ObjectRegistry
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListRequest,
    ObjectListResponse,
)
from app.objects.types import ObjectTypes
from app.utils.sqids import Sqid


@get("/{object_type:str}/{id:str}")
async def get_object_detail(
    request: Request,
    object_type: ObjectTypes,
    id: Sqid,
    transaction: AsyncSession,
) -> ObjectDetailDTO:
    """Get detailed object information."""
    object_service = ObjectRegistry.get_class(object_type)
    obj = await object_service.get_by_id(transaction, id)
    return object_service.to_detail_dto(obj)


@post("/{object_type:str}")
async def list_objects(
    request: Request,
    object_type: ObjectTypes,
    data: ObjectListRequest,
    transaction: AsyncSession,
) -> ObjectListResponse:
    """List objects with filtering and pagination."""
    object_service = ObjectRegistry.get_class(object_type)
    objects, total = await object_service.get_list(transaction, data)

    return ObjectListResponse(
        objects=[object_service.to_list_dto(obj) for obj in objects],
        total=total,
        limit=data.limit,
        offset=data.offset,
    )


# @post("/{object_type:str}/{id:str}/actions")
# async def perform_object_action(
#     object_type: str,
#     id: Sqid,
#     request: Request,
#     data: PerformActionRequest,
#     session: AsyncSession,
#     action_service: ActionService,
# ) -> Response:
#     """Perform an action on an object."""
#     obj = await get_object_by_id(session, object_type, id)
#     user_id = request.session.get("user_id")
#
#     await action_service.perform_action(
#         session=session,
#         obj=obj,
#         action_name=data.action,
#         user_id=user_id,
#         object_version=data.object_version,
#         idempotency_key=data.idempotency_key,
#         context=data.context,
#     )
#     return Response(content="Action completed", status_code=200)
#


# Object router
object_router = Router(
    path="/o",
    route_handlers=[
        get_object_detail,
        list_objects,
        # perform_object_action,
    ],
    tags=["objects"],
)
