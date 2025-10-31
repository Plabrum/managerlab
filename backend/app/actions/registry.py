from typing import Any, Self

from app.actions.base import ActionGroup, BaseAction
from app.actions.enums import ActionGroupType
from app.base.registry import BaseRegistry


class ActionRegistry(
    BaseRegistry[ActionGroupType, ActionGroup],
):
    _flat_registry: dict[str, type[BaseAction]]
    _struct_to_action: dict[type, type[BaseAction]]

    def __new__(cls: type[Self], **dependencies: Any) -> Self:
        inst = super().__new__(cls, **dependencies)
        # Only initialize flat registry if it doesn't exist (singleton pattern)
        if not hasattr(inst, "_flat_registry"):
            inst._flat_registry = {}
        if not hasattr(inst, "_struct_to_action"):
            inst._struct_to_action = {}
        return inst

    def register(
        self,
        action_group_type: ActionGroupType,
        action_group: ActionGroup,
    ) -> None:
        self._registry[action_group_type] = action_group

    def register_action(self, action_key: str, action_class: type[BaseAction]) -> None:
        self._flat_registry[action_key] = action_class
