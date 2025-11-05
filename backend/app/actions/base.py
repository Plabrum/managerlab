import inspect
from abc import ABC
from enum import StrEnum
from typing import Any, ClassVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.actions.enums import ActionGroupType, ActionIcon
from app.actions.registry import ActionRegistry
from app.actions.schemas import (
    ActionDTO,
    ActionExecutionResponse,
)
from app.base.models import BaseDBModel


def _filter_kwargs_by_signature(func: Any, available_kwargs: dict[str, Any]) -> dict[str, Any]:
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


class BaseAction(ABC):
    """Base class for all actions in the platform.

    Subclasses must implement an execute() classmethod with their specific signature.
    The execute method will be called with filtered kwargs based on its signature.
    """

    action_key: ClassVar[StrEnum]
    label: ClassVar[str]  # Display label
    is_bulk_allowed: ClassVar[bool] = False
    priority: ClassVar[int] = 100  # Display priority (lower = higher priority)
    icon: ClassVar[ActionIcon] = ActionIcon.default
    confirmation_message: ClassVar[str | None] = None  # Optional confirmation message
    should_redirect_to_parent: ClassVar[bool] = False  # Whether to redirect to parent after execution

    # Model and load options for default get_object implementation
    model: ClassVar[type[BaseDBModel] | None] = None
    load_options: ClassVar[list[ExecutableOption]] = []

    @classmethod
    async def get_object(
        cls,
        object_id: int,
        transaction: AsyncSession,
    ) -> BaseDBModel | None:
        if cls.model is None:
            return None

        result = await transaction.execute(
            select(cls.model).where(cls.model.id == object_id).options(*cls.load_options)
        )
        return result.scalar_one()

    @classmethod
    def is_available(  # type: ignore[override]
        cls,
        obj: BaseDBModel | None,
        **kwargs: Any,
    ) -> bool:
        return True

    @classmethod
    async def execute(cls, obj, **kwargs: Any) -> ActionExecutionResponse:
        """Execute the action and return the affected database model object."""
        raise NotImplementedError(f"{cls.__name__} must implement execute()")


class ActionGroup:
    def __init__(
        self,
        group_type: ActionGroupType,
        action_registry: Any,  # ActionRegistry - forward ref to avoid circular import
        model_type: type[BaseDBModel] | None,
        default_invalidation: str | None = None,
        load_options: list[ExecutableOption] | None = None,
    ) -> None:
        self.group_type = group_type
        self.actions: dict[str, type[BaseAction]] = {}
        self.action_registry = action_registry
        self.model_type = model_type
        self._execute_union: type | None = None
        self.default_invalidation = default_invalidation
        self.load_options = load_options or []

    def __call__(self, action_class: type[BaseAction]) -> type[BaseAction]:
        action_class.model = self.model_type
        action_key = action_class.action_key
        combined_key = self._get_action_key(action_key)
        self.actions[combined_key] = action_class
        self.action_registry.register_action(combined_key, action_class)
        return action_class

    def _get_action_key(self, action_key: str) -> str:
        return f"{self.group_type.value}__{action_key.replace('.', '_')}"

    def get_action(self, action_key: str) -> type[BaseAction]:
        if action_key not in self.actions:
            raise Exception("Unknown action type")
        return self.actions[action_key]

    async def get_object(self, object_id: int) -> BaseDBModel | None:
        """Get object by ID using the action group's model type."""
        if self.model_type is None:
            raise Exception("This action group has no associated model type")

        transaction = self.action_registry.dependencies["transaction"]

        result = await transaction.execute(
            select(self.model_type).where(self.model_type.id == object_id).options(*self.load_options)
        )
        return result.scalar_one()

    async def trigger(
        self,
        data: Any,  # Discriminated union instance
        object_id: int | None = None,
    ) -> ActionExecutionResponse:
        action_class: BaseAction = self.action_registry._struct_to_action[type(data)]
        obj = (
            await action_class.get_object(
                object_id=object_id,
                transaction=self.action_registry.dependencies["transaction"],
            )
            if object_id
            else None
        )

        # Inspect the signature once
        sig = inspect.signature(action_class.execute)
        params = sig.parameters

        # Prepare possible arguments
        candidate_args = {
            "obj": obj,
            "data": getattr(data, "data", data),
            **self.action_registry.dependencies,
        }

        # Filter only those accepted by the execute() signature
        filtered_kwargs = {name: val for name, val in candidate_args.items() if name in params}

        # Execute action and get the resulting object
        actions_execution_response = await action_class.execute(**filtered_kwargs)
        if not actions_execution_response.invalidate_queries and self.default_invalidation:
            actions_execution_response.invalidate_queries.append(self.default_invalidation)
        return actions_execution_response

    def get_available_actions(
        self,
        obj: BaseDBModel | None = None,
    ) -> list[ActionDTO]:
        available = []
        for action_key, action_class in self.actions.items():
            # Filter dependencies to only those accepted by is_available method
            filtered_kwargs = _filter_kwargs_by_signature(action_class.is_available, self.action_registry.dependencies)
            if action_class.is_available(obj, **filtered_kwargs):
                available.append((action_key, action_class))

        # Sort by priority
        available.sort(key=lambda x: x[1].priority)

        # Transform to DTOs
        return [
            ActionDTO(
                action_group_type=self.group_type,
                action=action_key,
                label=action_class.label,
                is_bulk_allowed=action_class.is_bulk_allowed,
                priority=action_class.priority,
                icon=action_class.icon.value if action_class.icon else None,
                confirmation_message=action_class.confirmation_message,
                should_redirect_to_parent=action_class.should_redirect_to_parent,
            )
            for action_key, action_class in available
        ]


def action_group_factory[T: BaseDBModel](
    group_type: ActionGroupType,
    default_invalidation: str | None = None,
    model_type: type[T] | None = None,
    load_options: list[ExecutableOption] | None = None,
) -> ActionGroup:
    registry = ActionRegistry()
    action_group = ActionGroup(
        group_type=group_type,
        action_registry=registry,
        model_type=model_type,
        default_invalidation=default_invalidation,
        load_options=load_options,
    )
    # Register the action group with the registry
    registry.register(group_type, action_group)

    return action_group
