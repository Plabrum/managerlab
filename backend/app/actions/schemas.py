from typing import Any
from app.actions.enums import ActionGroupType
from app.base.schemas import BaseSchema
from app.utils.sqids import Sqid


class ActionDTO(BaseSchema):
    action: str
    label: str
    is_bulk_allowed: bool = False
    available: bool = True
    priority: int = 100
    icon: str | None = None
    confirmation_message: str | None = None


class ActionExecutionRequest(BaseSchema):
    action_group: ActionGroupType
    object_id: Sqid


class ActionExecutionResponse(BaseSchema):
    success: bool
    message: str
    results: dict[str, Any] = {}


class ActionListResponse(BaseSchema):
    actions: list[ActionDTO]
