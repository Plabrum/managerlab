from litestar import Router, get, post

from app.actions.registry import ActionRegistry
from app.actions.schemas import (
    ActionListResponse,
    ActionExecutionResponse,
    build_action_union,
)
from app.actions.enums import ActionGroupType
from app.utils.sqids import Sqid, sqid_decode
from app.utils.discovery import discover_and_import

discover_and_import(["actions.py", "top_level_actions.py"], base_path="app")


# ----------------------------
# GET: list actions (no object)
# ----------------------------
@get("/{action_group:str}")
async def list_actions(
    action_group: ActionGroupType,
    action_registry: ActionRegistry,
) -> ActionListResponse:
    """List available top-level actions for a group (no object context)."""
    action_group_instance = action_registry.get_class(action_group)
    available_actions = action_group_instance.get_available_actions(None)

    return ActionListResponse(actions=available_actions)


# -----------------------------------------
# GET: list actions for a specific *object*
# -----------------------------------------
@get("/{action_group:str}/{object_id:str}")
async def list_object_actions(
    action_group: ActionGroupType,
    object_id: Sqid,
    action_registry: ActionRegistry,
) -> ActionListResponse:
    """List available actions for a specific object within a group."""
    action_group_instance = action_registry.get_class(action_group)
    object = await action_group_instance.get_object(sqid_decode(object_id))
    available_actions = action_group_instance.get_available_actions(object)

    return ActionListResponse(actions=available_actions)


# Create the Action union type from all registered actions
Action = build_action_union(ActionRegistry())


# --------------------------------
# POST: execute group-level action
# --------------------------------
@post("/{action_group:str}")
async def execute_action(
    action_group: ActionGroupType,
    data: Action,  # type: ignore [valid-type]
    action_registry: ActionRegistry,
) -> ActionExecutionResponse:
    action_group_instance = action_registry.get_class(action_group)
    return await action_group_instance.trigger(
        object_id=None,
        data=data,
    )


# ----------------------------------------
# POST: execute action for a specific item
# ----------------------------------------
@post("/{action_group:str}/{object_id:str}")
async def execute_object_action(
    action_group: ActionGroupType,
    object_id: Sqid,
    data: Action,  # type: ignore [valid-type]
    action_registry: ActionRegistry,
) -> ActionExecutionResponse:
    """Execute an action in the context of a specific object."""
    action_group_instance = action_registry.get_class(action_group)
    return await action_group_instance.trigger(
        object_id=sqid_decode(object_id),
        data=data,
    )


# Router mount (handler paths above are relative; no "/actions" duplication)
action_router = Router(
    path="/actions",
    route_handlers=[
        list_actions,
        list_object_actions,
        execute_action,
        execute_object_action,
    ],
    tags=["actions"],
)
