import inspect
import sys
from functools import reduce
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    TypeAliasType,
    get_args,
    get_origin,
    get_type_hints,
)

import msgspec
from litestar.dto.base_dto import AbstractDTO

from app.actions.enums import ActionGroupType, ActionResultType
from app.base.schemas import BaseSchema
from app.utils.dto import dto_to_msgspec_struct_from_mapper
from app.utils.sqids import Sqid

if TYPE_CHECKING:
    from app.actions.registry import ActionRegistry


class ActionDTO(BaseSchema):
    action: str
    label: str
    action_group_type: ActionGroupType
    is_bulk_allowed: bool = False
    available: bool = True
    priority: int = 100
    icon: str | None = None
    confirmation_message: str | None = None
    should_redirect_to_parent: bool = False


class ActionExecutionRequest(BaseSchema):
    action_group: ActionGroupType
    object_id: Sqid


class RedirectActionResult(BaseSchema, tag=ActionResultType.redirect.value):
    path: str  # e.g., "/brands/abc123" or ".." for parent


class DownloadFileActionResult(BaseSchema, tag=ActionResultType.download_file.value):
    url: str
    filename: str


ActionResult = RedirectActionResult | DownloadFileActionResult


class ActionExecutionResponse(BaseSchema):
    """Response from action execution with metadata for navigation and query invalidation."""

    message: str = ""
    invalidate_queries: list[str] = []  # Query keys to invalidate
    action_result: ActionResult | None = None  # Frontend action to perform


class ActionListResponse(BaseSchema):
    actions: list[ActionDTO]


# --- Helper functions for Action union generation -------------------------------


def _base_type(tp: Any) -> Any:
    """Extract base type from Annotated types."""
    return get_args(tp)[0] if get_origin(tp) is Annotated else tp


def is_dto(tp: Any) -> bool:
    """Return True when the provided type is a Litestar DTO subclass."""
    if tp is None:
        return False

    if isinstance(tp, TypeAliasType):
        alias_value = getattr(tp, "__value__", None)
        return is_dto(alias_value)

    origin = get_origin(tp)
    if origin is not None:
        # Support Type[SomeDTO] and similar wrappers by checking innermost arg
        if origin is type and get_args(tp):
            return is_dto(get_args(tp)[0])
        return False

    return inspect.isclass(tp) and issubclass(tp, AbstractDTO)


def default_tp(tp: Any | None) -> list[tuple[str, Any]]:
    """Return struct field definitions for the provided type."""
    if tp is None or tp is inspect._empty:
        return []
    if isinstance(tp, TypeAliasType):
        tp = getattr(tp, "__value__", tp)
    return [("data", tp)]


def _extract_data_param_type(action_cls: type) -> Any | None:
    """Extract the type annotation of the 'data' parameter from an action's execute method.

    Args:
        action_cls: The action class to inspect

    Returns:
        The type annotation of the 'data' parameter, or None if no data parameter exists
    """
    meth = getattr(action_cls, "execute")
    fn = meth.__func__ if isinstance(meth, classmethod | staticmethod) else meth
    fn = inspect.unwrap(fn)

    sig = inspect.signature(fn)
    if "data" not in sig.parameters:
        return None

    mod = sys.modules.get(action_cls.__module__)
    hints = get_type_hints(
        fn,
        globalns=getattr(mod, "__dict__", {}),
        localns=vars(action_cls),
        include_extras=True,
    )
    ann = hints.get("data", sig.parameters["data"].annotation)
    if ann is inspect._empty:
        raise TypeError(f"{action_cls.__name__}.execute 'data' is unannotated")
    return _base_type(ann)


def build_action_union(action_registry: "ActionRegistry") -> TypeAliasType:
    """Build a discriminated union type from all registered actions.

    This function iterates through all registered actions, extracts their data parameter
    types, converts them to msgspec structs, and creates a discriminated union with
    tag-based discrimination using the action key.

    Args:
        action_registry: The ActionRegistry instance containing all registered actions

    Returns:
        A TypeAliasType representing the union of all action struct types
    """

    action_structs: list[type[msgspec.Struct]] = []

    for action_key, action_cls in action_registry._flat_registry.items():
        tp = _extract_data_param_type(action_cls)
        tp_schema = dto_to_msgspec_struct_from_mapper(tp) if tp and is_dto(tp) else tp

        fields = default_tp(tp_schema)

        # Create a tagged struct for this action, optionally including a data field
        struct_class = msgspec.defstruct(
            f"{action_cls.__name__}Action",
            fields,
            tag_field="action",
            tag=action_key,
        )
        action_structs.append(struct_class)

        # Register the mapping from struct type to action class
        action_registry._struct_to_action[struct_class] = action_cls

    # Build union type from all action structs
    _action_union = (
        reduce(lambda a, b: a | b, action_structs) if action_structs else msgspec.Struct  # type: ignore[arg-type, return-value]
    )
    return TypeAliasType("Action", _action_union)  # type: ignore[valid-type]
