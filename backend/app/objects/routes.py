"""Generic object routes and endpoints."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from litestar import Router, get, post, Request

from app.base.models import BaseDBModel
from app.objects.base import ObjectRegistry
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListRequest,
    ObjectListResponse,
)
from app.objects.enums import ObjectTypes
from app.utils.sqids import Sqid, sqid_decode


@get("/{object_type:str}/{id:str}")
async def get_object_detail(
    request: Request,
    object_type: ObjectTypes,
    id: Sqid,
    transaction: AsyncSession,
) -> ObjectDetailDTO:
    """Get detailed object information."""
    request.app.logger.info(f"data:{id}, object_type:{object_type}")
    object_service = ObjectRegistry.get_class(object_type)
    obj: BaseDBModel = await object_service.get_by_id(transaction, sqid_decode(id))
    return object_service.to_detail_dto(obj)


@post("/{object_type:str}", operation_id="list_objects")
async def list_objects(
    request: Request,
    object_type: ObjectTypes,
    data: ObjectListRequest,
    transaction: AsyncSession,
) -> ObjectListResponse:
    """List objects with filtering and pagination."""
    request.app.logger.info(f"data:{data}")
    object_service = ObjectRegistry.get_class(object_type)
    objects: Sequence[BaseDBModel]
    objects, total = await object_service.get_list(transaction, data)
    columns = object_service.column_definitions

    return ObjectListResponse(
        objects=[object_service.to_list_dto(obj) for obj in objects],
        total=total,
        limit=data.limit,
        offset=data.offset,
        columns=columns,
        actions=object_service.get_list_actions(),
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
