"""Generic object routes and endpoints."""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from litestar import Router, get, post, Request
from litestar.di import Provide

from app.objects.query import get_object_by_sqid, query_objects
from app.objects.services.base import ObjectService
from app.actions.services import ActionService
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListRequest,
    ObjectListResponse,
    PerformActionRequest,
    PerformActionResult,
    StateDTO,
)


@get("/{object_type:str}/{sqid:str}")
async def get_object_detail(
    object_type: str,
    sqid: str,
    request: Request,
    session: AsyncSession,
    object_service: ObjectService,
) -> ObjectDetailDTO:
    """Get detailed object information."""
    obj = await get_object_by_sqid(session, object_type, sqid)
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


@get("/{object_type:str}/{sqid:str}/actions")
async def get_object_actions(
    object_type: str,
    sqid: str,
    request: Request,
    session: AsyncSession,
    action_service: ActionService,
) -> list[Dict[str, Any]]:
    """Get available actions for an object."""
    obj = await get_object_by_sqid(session, object_type, sqid)
    user_id = request.session.get("user_id")

    return await action_service.get_available_actions(
        session=session, obj=obj, user_id=user_id
    )


@post("/{object_type:str}/{sqid:str}/actions")
async def perform_object_action(
    object_type: str,
    sqid: str,
    request: Request,
    data: PerformActionRequest,
    session: AsyncSession,
    action_service: ActionService,
) -> PerformActionResult:
    """Perform an action on an object."""
    obj = await get_object_by_sqid(session, object_type, sqid)
    user_id = request.session.get("user_id")

    result = await action_service.perform_action(
        session=session,
        obj=obj,
        action_name=data.action,
        user_id=user_id,
        object_version=data.object_version,
        idempotency_key=data.idempotency_key,
        context=data.context,
    )

    # Convert result to DTO
    new_state_dto = None
    if result["new_state"]:
        new_state_dto = StateDTO(
            key=result["new_state"], label=result["new_state"].replace("_", " ").title()
        )

    return PerformActionResult(
        success=result["success"],
        result=result["result"],
        new_state=new_state_dto,
        updated_fields=result["updated_fields"],
        object_version=obj.object_version if result["success"] else None,
    )


# Object router
object_router = Router(
    path="/o",
    route_handlers=[
        get_object_detail,
        list_objects,
        get_object_actions,
        perform_object_action,
    ],
    dependencies={
        "object_service": Provide(lambda: ObjectService(), sync_to_thread=False),
        "action_service": Provide(lambda: ActionService(), sync_to_thread=False),
    },
    tags=["objects"],
)
