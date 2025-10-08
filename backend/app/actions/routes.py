from litestar import Router, get, post
from app.utils.discovery import discover_and_import
from app.actions.schema_generator import generate_all_action_schemas
from app.utils.sqids import Sqid
from app.actions.registry import ActionRegistry
from app.actions.schemas import (
    ActionDTO,
    ActionListResponse,
    ActionExecutionResponse,
)
from app.actions.enums import ActionGroupType
from app.utils.sqids import sqid_decode

discover_and_import(["actions.py", "top_level_actions.py"], base_path="app")

ActionData = generate_all_action_schemas()


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
    available_actions = await action_group_instance.get_available_actions(None)

    return ActionListResponse(
        actions=[
            ActionDTO(
                action=action_key,
                label=action_class.label,
                is_bulk_allowed=action_class.is_bulk_allowed,
                priority=action_class.priority,
                icon=action_class.icon.value if action_class.icon else None,
                confirmation_message=action_class.confirmation_message,
            )
            for action_key, action_class in available_actions
        ]
    )


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
    available_actions = await action_group_instance.get_available_actions(
        sqid_decode(object_id)
    )

    return ActionListResponse(
        actions=[
            ActionDTO(
                action=action_key,
                label=action_class.label,
                is_bulk_allowed=action_class.is_bulk_allowed,
                priority=action_class.priority,
                icon=action_class.icon.value if action_class.icon else None,
                confirmation_message=action_class.confirmation_message,
            )
            for action_key, action_class in available_actions
        ]
    )


# --------------------------------
# POST: execute group-level action
# --------------------------------
@post("/{action_group:str}")
async def execute_action(
    action_group: ActionGroupType,
    data: ActionData,
    action_registry: ActionRegistry,
) -> ActionExecutionResponse:
    """Execute a top-level action (no object context)."""
    action_group_instance = action_registry.get_class(action_group)
    return await action_group_instance.trigger(
        object_id=None,
        action_data=data.action_data,
    )


# ----------------------------------------
# POST: execute action for a specific item
# ----------------------------------------
@post("/{action_group:str}/{object_id:str}")
async def execute_object_action(
    action_group: ActionGroupType,
    object_id: Sqid,
    data: ActionData,
    action_registry: ActionRegistry,
) -> ActionExecutionResponse:
    """Execute an action in the context of a specific object."""
    action_group_instance = action_registry.get_class(action_group)
    return await action_group_instance.trigger(
        object_id=sqid_decode(object_id),
        action_data=data.action_data,
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
