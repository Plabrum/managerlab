"""Actions platform for executing operations on domain objects."""

from app.actions.base import ActionGroup, BaseAction, action_group_factory
from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.actions.schemas import (
    ActionDTO,
    ActionExecutionRequest,
    ActionExecutionResponse,
)

__all__ = [
    "BaseAction",
    "ActionRegistry",
    "ActionGroup",
    "action_group_factory",
    "ActionDTO",
    "ActionExecutionRequest",
    "ActionExecutionResponse",
    "ActionGroupType",
]
