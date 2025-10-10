from typing import Any, TypeAliasType, Annotated, get_args, get_origin, get_type_hints
from functools import reduce
import inspect
import sys

import msgspec

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


# --- Helper functions for Action union generation -------------------------------


def _base_type(tp: Any) -> Any:
    """Extract base type from Annotated types."""
    return get_args(tp)[0] if get_origin(tp) is Annotated else tp


def _extract_data_param_type(action_cls: type) -> Any | None:
    """Extract the type annotation of the 'data' parameter from an action's execute method.

    Args:
        action_cls: The action class to inspect

    Returns:
        The type annotation of the 'data' parameter, or None if no data parameter exists
    """
    meth = getattr(action_cls, "execute")
    fn = meth.__func__ if isinstance(meth, (classmethod, staticmethod)) else meth
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


def build_action_union(action_registry) -> TypeAliasType:
    """Build a discriminated union type from all registered actions.

    This function iterates through all registered actions, extracts their data parameter
    types, converts them to msgspec structs, and creates a discriminated union with
    tag-based discrimination using the action key.

    Args:
        action_registry: The ActionRegistry instance containing all registered actions

    Returns:
        A TypeAliasType representing the union of all action struct types
    """
    from app.utils.dto import dto_to_msgspec_struct_from_mapper

    action_structs: list[type[msgspec.Struct]] = []

    for action_key, action_cls in action_registry._flat_registry.items():
        tp = _extract_data_param_type(action_cls)
        if tp is None:
            continue

        # Convert DTO to msgspec struct
        tp = dto_to_msgspec_struct_from_mapper(tp)

        # Create a tagged struct for this action
        action_structs.append(
            msgspec.defstruct(
                f"{action_cls.__name__}Action",
                [("data", tp)],  # Must be a list of tuples, not a dict
                tag_field="action",
                tag=action_key,
            )
        )

    # Build union type from all action structs
    _action_union = (
        reduce(lambda a, b: a | b, action_structs) if action_structs else msgspec.Struct
    )
    return TypeAliasType("Action", _action_union)  # type: ignore[valid-type]
