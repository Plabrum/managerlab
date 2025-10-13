from typing import Self, Type, Dict, Any

from app.base.registry import BaseRegistry
from app.actions.base import BaseAction, ActionGroup
from app.actions.enums import ActionGroupType


class ActionRegistry(
    BaseRegistry[ActionGroupType, ActionGroup],
):
    _flat_registry: Dict[str, Type[BaseAction]]
    _struct_to_action: Dict[type, Type[BaseAction]]

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

    def register_action(self, action_key: str, action_class: Type[BaseAction]) -> None:
        self._flat_registry[action_key] = action_class
