from typing import Self, Type, Dict, Any
import inspect

from app.base.registry import BaseRegistry
from app.actions.base import BaseAction
from app.actions.enums import ActionGroupType
from app.base.models import BaseDBModel
from app.actions.schemas import ActionExecutionResponse, ActionDTO


def _filter_kwargs_by_signature(
    func: Any, available_kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """Filter kwargs to only include parameters that the function accepts.

    Args:
        func: The function/method to inspect
        available_kwargs: Dict of all available keyword arguments

    Returns:
        Dict containing only the kwargs that the function accepts
    """
    # Handle classmethods by unwrapping to get the actual function
    if isinstance(func, classmethod):
        func = func.__func__

    sig = inspect.signature(func)
    accepted_params = set(sig.parameters.keys())

    # Remove 'cls' or 'self' from accepted params as they're implicit
    accepted_params.discard("cls")
    accepted_params.discard("self")

    # If function accepts **kwargs, return all available kwargs
    for param in sig.parameters.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return available_kwargs

    # Otherwise, filter to only accepted parameters
    return {k: v for k, v in available_kwargs.items() if k in accepted_params}


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
        data: Any,  # Untyped - accepts the discriminated union from routes
        object_id: int | None = None,
    ) -> ActionExecutionResponse:
        obj = await self.get_object(object_id=object_id)
        action_class = self.get_action(data.action)

        # Filter dependencies to only those accepted by execute method
        filtered_kwargs = _filter_kwargs_by_signature(
            action_class.execute, self.action_registry.dependencies
        )

        # Check if execute method expects 'data' parameter
        sig = inspect.signature(action_class.execute)
        if "data" in sig.parameters:
            return await action_class.execute(obj, data=data, **filtered_kwargs)
        else:
            return await action_class.execute(obj, **filtered_kwargs)

    def get_available_actions(
        self,
        obj: BaseDBModel | None = None,
    ) -> list[ActionDTO]:
        available = []
        for action_key, action_class in self.actions.items():
            # Filter dependencies to only those accepted by is_available method
            filtered_kwargs = _filter_kwargs_by_signature(
                action_class.is_available, self.action_registry.dependencies
            )
            if action_class.is_available(obj, **filtered_kwargs):
                available.append((action_key, action_class))

        # Sort by priority
        available.sort(key=lambda x: x[1].priority)

        # Transform to DTOs
        return [
            ActionDTO(
                action=action_key,
                label=action_class.label,
                is_bulk_allowed=action_class.is_bulk_allowed,
                priority=action_class.priority,
                icon=action_class.icon.value if action_class.icon else None,
                confirmation_message=action_class.confirmation_message,
            )
            for action_key, action_class in available
        ]


#
# def create_default_delete_action() -> type[BaseAction]:
#     class DefaultDelete(BaseAction):
#         action_key = "delete"
#         label = "Delete"
#         is_bulk_allowed = True
#         priority = 0
#         icon = ActionIcon.trash
#         confirmation_message = "Are you sure you want to delete this item?"
#
#         @classmethod
#         async def execute(
#             cls,
#             obj: BaseDBModel,
#             transaction: AsyncSession,
#             **kwargs: Any,
#         ) -> ActionExecutionResponse:
#             if transaction:
#                 await transaction.delete(obj)
#             return ActionExecutionResponse(
#                 success=True,
#                 message="Deleted item",
#                 results={},
#             )
#
#     DefaultDelete.__name__ = "Delete"
#     return DefaultDelete
#
#
# def create_default_update_action[T: BaseDBModel](
#     model_type: Type[T], update_dto: Type[SQLAlchemyDTO[T]]
# ) -> type[BaseAction]:
#     class DefaultUpdate(BaseAction):
#         action_key = "update"
#         label = "Update"
#         is_bulk_allowed = True
#         priority = 50
#         icon = ActionIcon.edit
#
#         dto_class = update_dto
#         model_class = model_type
#
#         @classmethod
#         async def execute(
#             cls,
#             obj: T,
#             data: Any,
#             transaction: AsyncSession,
#             **kwargs: Any,  # Accept additional kwargs
#         ) -> ActionExecutionResponse:
#             # Extract the actual data from action_data
#             # action_data should have the update fields (excluding 'action' field)
#             if hasattr(data, "__dict__"):
#                 # Convert action_data to dict, excluding the 'action' field
#                 update_data = {
#                     k: v
#                     for k, v in data.__dict__.items()
#                     if k != "action" and not k.startswith("_")
#                 }
#             else:
#                 update_data = data if isinstance(data, dict) else {}
#
#             # Create DTOData instance with the update data
#             dto_data = DTOData[cls.dto_class](update_data)
#
#             # Apply updates to the model instance
#             for field, value in dto_data.as_builtins().items():
#                 if hasattr(obj, field):
#                     setattr(obj, field, value)
#
#             transaction.add(obj)
#
#             return ActionExecutionResponse(
#                 success=True,
#                 message="Updated item",
#                 results={},
#             )
#
#     DefaultUpdate.__name__ = f"Update{model_type.__name__}"
#     return DefaultUpdate
#
#
# def create_default_create_action[T: BaseDBModel](
#     model_type: Type[T], create_dto: Type[SQLAlchemyDTO[T]]
# ) -> type[BaseAction]:
#     class DefaultCreate(BaseAction):
#         action_key = "create"
#         label = "Create"
#         is_bulk_allowed = False
#         priority = 100
#         icon = ActionIcon.add
#
#         dto_class = create_dto
#         model_class = model_type
#
#         @classmethod
#         async def execute(
#             cls,
#             obj: T | None,
#             data: create_dto,
#             transaction: AsyncSession,
#             **kwargs: Any,  # Accept additional kwargs
#         ) -> ActionExecutionResponse:
#             new_obj = model_type(**data.as_builtins())
#             transaction.add(new_obj)
#             return ActionExecutionResponse(
#                 success=True,
#                 message="Created item",
#                 results={},
#             )
#
#         @classmethod
#         def is_available(cls, obj: T | None, **kwargs: Any) -> bool:
#             # Create action is available when there's no object (i.e., creating new)
#             return obj is None
#
#     DefaultCreate.__name__ = f"Create{model_type.__name__}"
#     return DefaultCreate
#


def action_group_factory[T: BaseDBModel](
    group_type: ActionGroupType,
    model_type: Type[T] | None = None,
    # include_delete: bool = True,
    # include_update: bool = True,
    # include_create: bool = False,  # Add option for create action
    # update_dto: Type[SQLAlchemyDTO[T]] | None = None,
    # create_dto: Type[SQLAlchemyDTO[T]] | None = None,
) -> ActionGroup:
    registry = ActionRegistry()
    action_group = ActionGroup(group_type, registry, model_type)

    # if include_delete and model_type:
    #     delete_action = create_default_delete_action()
    #     action_group(delete_action)
    #
    # if include_update and model_type and update_dto is not None:
    #     update_action = create_default_update_action(model_type, update_dto=update_dto)
    #     action_group(update_action)
    #
    # if include_create and model_type and create_dto is not None:
    #     create_action = create_default_create_action(model_type, create_dto=create_dto)
    #     action_group(create_action)

    # Register the action group with the registry
    registry.register(group_type, action_group)

    return action_group
