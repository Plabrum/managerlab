from abc import ABC
from enum import StrEnum
from typing import TYPE_CHECKING, Any, ClassVar

from litestar.exceptions import NotFoundException
from msgspec import Struct
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
from app.utils.tracing import trace_operation

if TYPE_CHECKING:
    from opentelemetry.trace import Span

    from app.actions.deps import ActionDeps


def _enrich_action_span(span: "Span", args: tuple, kwargs: dict) -> None:
    """Enrich action execution spans with action-specific context."""
    if args and isinstance(args[0], ActionGroup):
        action_group = args[0]
        span.set_attribute("action.group", action_group.group_type.value)

    if object_id := kwargs.get("object_id"):
        span.set_attribute("action.object_id", object_id)


class EmptyActionData(Struct):
    """Empty struct for actions that don't require any data."""

    pass


class BaseAction[O: BaseDBModel, D: Struct](ABC):
    """Base class for all actions - shared attributes and methods.

    Type parameters:
        O: The database model type this action operates on
        D: The msgspec Struct type for action data/schema

    Use BaseObjectAction for actions that operate on existing objects.
    Use BaseTopLevelAction for actions that don't require an existing object (e.g., create).
    """

    action_key: ClassVar[StrEnum]
    label: ClassVar[str]  # Display label
    is_bulk_allowed: ClassVar[bool] = False
    priority: ClassVar[int] = 100  # Display priority (lower = higher priority)
    icon: ClassVar[ActionIcon] = ActionIcon.default
    confirmation_message: ClassVar[str | None] = None  # Optional confirmation message
    should_redirect_to_parent: ClassVar[bool] = False  # Whether to redirect to parent after execution
    is_hidden: ClassVar[bool] = False  # Hidden actions are not shown in dropdown but can still be executed

    # Model and load options for default get_object implementation
    model: ClassVar[type[BaseDBModel] | None] = None
    load_options: ClassVar[list[ExecutableOption]] = []

    @classmethod
    async def get_object(
        cls,
        object_id: int,
        transaction: AsyncSession,
    ) -> O | None:
        if cls.model is None:
            return None

        result = await transaction.execute(
            select(cls.model).where(cls.model.id == object_id).options(*cls.load_options)
        )
        return result.scalar_one()  # type: ignore[return-value]

    @classmethod
    def is_available(
        cls,
        obj: O | None,
        deps: "ActionDeps",
    ) -> bool:
        return True


class BaseObjectAction[O: BaseDBModel, D: Struct](BaseAction[O, D]):
    """Base class for actions that operate on existing database objects.

    Type parameters:
        O: The database model type this action operates on
        D: The msgspec Struct type for action data/schema

    Example: DeleteBrand, UpdateCampaign, PublishDeliverable

    Subclasses must implement:
        async def execute(cls, obj: O, data: D, transaction: AsyncSession)
    """

    @classmethod
    async def execute(
        cls,
        obj: O,
        data: D,
        transaction: AsyncSession,
        deps: "ActionDeps",
    ) -> ActionExecutionResponse:
        """Execute the action on an existing object.

        Args:
            obj: The database object this action operates on (never None)
            data: The action's input data (msgspec struct from discriminated union)
            transaction: Database session for this request (auto-commits via SQLAlchemy plugin)
            deps: Injected dependencies (user, team_id, s3_client, etc.)

        Returns:
            ActionExecutionResponse with result metadata
        """
        raise NotImplementedError(f"{cls.__name__} must implement execute()")


class BaseTopLevelAction[D: Struct](BaseAction[BaseDBModel, D]):
    """Base class for actions that don't operate on existing objects.

    Type parameters:
        D: The msgspec Struct type for action data/schema

    Example: CreateBrand, CreateCampaign, RegisterMedia

    Subclasses must implement:
        async def execute(cls, data: D, transaction: AsyncSession)
    """

    @classmethod
    async def execute(
        cls,
        data: D,
        transaction: AsyncSession,
        deps: "ActionDeps",
    ) -> ActionExecutionResponse:
        """Execute the action without an existing object.

        Args:
            data: The action's input data (msgspec struct from discriminated union)
            transaction: Database session for this request (auto-commits via SQLAlchemy plugin)
            deps: Injected dependencies (user, team_id, s3_client, etc.)

        Returns:
            ActionExecutionResponse with result metadata
        """
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
        self.object_actions: dict[str, type[BaseObjectAction]] = {}
        self.top_level_actions: dict[str, type[BaseTopLevelAction]] = {}
        self.action_registry = action_registry
        self.model_type = model_type
        self._execute_union: type | None = None
        self.default_invalidation = default_invalidation
        self.load_options = load_options or []

    def __call__(self, action_class: type[BaseAction]) -> type[BaseAction]:
        action_class.model = self.model_type
        action_key = action_class.action_key
        combined_key = self._get_action_key(action_key)

        # Register in main actions dict
        self.actions[combined_key] = action_class

        # Classify into appropriate type-specific dictionary
        if issubclass(action_class, BaseObjectAction):
            self.object_actions[combined_key] = action_class  # type: ignore[assignment]
        elif issubclass(action_class, BaseTopLevelAction):
            self.top_level_actions[combined_key] = action_class  # type: ignore[assignment]

        self.action_registry.register_action(combined_key, action_class)
        return action_class

    def _get_action_key(self, action_key: str) -> str:
        return f"{self.group_type.value}__{action_key.replace('.', '_')}"

    def get_action(self, action_key: str) -> type[BaseAction]:
        if action_key not in self.actions:
            raise NotFoundException(detail=f"Action {action_key} not found")
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

    @trace_operation("action_execution", enrich=_enrich_action_span)
    async def trigger(
        self,
        data: Any,  # Discriminated union instance
        object_id: int | None = None,
    ) -> ActionExecutionResponse:
        """Execute an action with proper dependency injection."""
        from app.actions.deps import ActionDeps

        action_class: type[BaseAction] = self.action_registry._struct_to_action[type(data)]
        transaction = self.action_registry.dependencies["transaction"]

        # Create deps instance for this request
        deps = ActionDeps(**self.action_registry.dependencies)

        # Extract data from discriminated union wrapper
        action_data = getattr(data, "data", data)

        if issubclass(action_class, BaseObjectAction):
            # Instance action - requires object
            obj = await action_class.get_object(object_id=object_id, transaction=transaction) if object_id else None
            if obj is None:
                raise NotFoundException(detail=f"Object action {action_class.__name__} requires object_id")
            actions_execution_response = await action_class.execute(obj, action_data, transaction, deps)
        elif issubclass(action_class, BaseTopLevelAction):
            # Top-level action - no object needed
            actions_execution_response = await action_class.execute(action_data, transaction, deps)
        else:
            raise TypeError(f"Action {action_class.__name__} must inherit from BaseObjectAction or BaseTopLevelAction")

        # Add default invalidation if not specified
        if not actions_execution_response.invalidate_queries and self.default_invalidation:
            actions_execution_response.invalidate_queries.append(self.default_invalidation)

        return actions_execution_response

    def get_available_actions(
        self,
        obj: BaseDBModel | None = None,
    ) -> list[ActionDTO]:
        from app.actions.deps import ActionDeps

        # Select the appropriate pre-sorted dictionary
        actions_dict = self.top_level_actions if obj is None else self.object_actions

        # Create deps instance for this request
        deps = ActionDeps(**self.action_registry.dependencies)

        available = []
        for action_key, action_class in actions_dict.items():
            # Skip hidden actions (they can still be executed but won't show in dropdown)
            if action_class.is_hidden:
                continue
            if action_class.is_available(obj, deps):
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
