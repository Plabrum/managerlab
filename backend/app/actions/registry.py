from typing import Self, Type, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from app.base.registry import BaseRegistry
from app.actions.base import BaseAction
from app.actions.enums import ActionGroupType, ActionIcon
from app.base.models import BaseDBModel
from litestar.dto import DTOData
from app.actions.schemas import ActionExecutionResponse


class ActionRegistry(
    BaseRegistry[ActionGroupType, "ActionGroup"],
):
    _flat_registry: Dict[str, Type[BaseAction]]

    def __new__(cls: type[Self], **dependencies: Any) -> Self:
        inst = super().__new__(cls, **dependencies)
        # Only initialize flat registry if it doesn't exist (singleton pattern)
        if not hasattr(inst, "_flat_registry"):
            inst._flat_registry = {}
        return inst

    def register(
        self,
        action_group_type: ActionGroupType,
        action_group: "ActionGroup",
    ) -> None:
        self._registry[action_group_type] = action_group

    def register_action(self, action_key: str, action_class: Type[BaseAction]) -> None:
        self._flat_registry[action_key] = action_class


class ActionGroup:
    def __init__(
        self,
        group_type: ActionGroupType,
        action_registry: ActionRegistry,
        model_type: Type[BaseDBModel] | None,
    ) -> None:
        self.group_type = group_type
        self.actions: Dict[str, Type[BaseAction]] = {}
        self.action_registry = action_registry
        self.model_type = model_type
        self._execute_union: Type | None = None

    def __call__(self, action_class: Type[BaseAction]) -> Type[BaseAction]:
        action_key = action_class.action_key
        combined_key = f"{self.group_type.value}__{action_key.replace('.', '_')}"
        self.actions[action_key] = action_class
        self.action_registry.register_action(combined_key, action_class)
        return action_class

    def get_action(self, action_key: str) -> Type[BaseAction]:
        if action_key not in self.actions:
            raise Exception("Unknown action type")
        return self.actions[action_key]

    async def get_object(self, object_id: int | None) -> BaseDBModel | None:
        if object_id and self.model_type:
            transaction = self.action_registry.dependencies.get("transaction")
            if transaction:
                return await transaction.get(self.model_type, object_id)
        return None

    async def trigger(
        self,
        action_data: Any,  # Untyped - accepts the discriminated union from routes
        object_id: int | None = None,
    ) -> ActionExecutionResponse:
        obj = await self.get_object(object_id=object_id)
        action_class = self.get_action(action_data.action)
        return await action_class.execute(
            obj, action_data=action_data, **self.action_registry.dependencies
        )

    async def get_available_actions(
        self, object_id: int | None = None
    ) -> list[tuple[str, Type[BaseAction]]]:
        obj = await self.get_object(object_id=object_id)

        # Filter actions by availability
        available = [
            (action_key, action_class)
            for action_key, action_class in self.actions.items()
            if action_class.is_available(obj, **self.action_registry.dependencies)
        ]

        # Sort by priority
        available.sort(key=lambda x: x[1].priority)

        return available


def create_default_delete_action() -> Type[BaseAction]:
    class DefaultDelete(BaseAction):
        action_key = "delete"
        label = "Delete"
        is_bulk_allowed = True
        priority = 0
        icon = ActionIcon.trash
        confirmation_message = "Are you sure you want to delete this item?"

        @classmethod
        async def execute(
            cls,
            obj: BaseDBModel,
            transaction: AsyncSession,
        ) -> ActionExecutionResponse:
            await transaction.delete(obj)
            return ActionExecutionResponse(
                success=True,
                message="Deleted item",
                results={},
            )

    DefaultDelete.__name__ = "Delete"
    return DefaultDelete


def create_default_update_action() -> Type[BaseAction]:
    class DefaultUpdate(BaseAction):
        action_key = "update"
        label = "Update"
        is_bulk_allowed = True
        priority = 50
        icon = ActionIcon.edit

        @classmethod
        async def execute(
            cls,
            obj: BaseDBModel,
            data: DTOData[BaseDBModel],
            transaction: Any,
        ) -> ActionExecutionResponse:
            data.update_instance(obj)

            return ActionExecutionResponse(
                success=True,
                message="Updated item",
                results={},
            )

    DefaultUpdate.__name__ = "Update"
    return DefaultUpdate


def action_group_factory(
    group_type: ActionGroupType,
    model_type: Type[BaseDBModel] | None = None,
    include_delete: bool = True,
    include_update: bool = True,
) -> ActionGroup:
    registry = ActionRegistry()
    action_group = ActionGroup(group_type, registry, model_type)

    if include_delete and model_type:
        delete_action = create_default_delete_action()
        action_group(delete_action)

    if include_update and model_type:
        update_action = create_default_update_action()
        action_group(update_action)

    # Register the action group with the registry
    registry.register(group_type, action_group)

    return action_group
