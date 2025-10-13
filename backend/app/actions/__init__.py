"""Actions platform for executing operations on domain objects."""

from app.actions.base import BaseAction, ActionGroup, action_group_factory
from app.actions.registry import ActionRegistry
from app.actions.schemas import (
    ActionDTO,
    ActionExecutionRequest,
    ActionExecutionResponse,
)
from app.actions.enums import ActionGroupType

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
