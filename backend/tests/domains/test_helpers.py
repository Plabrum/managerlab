"""Shared test utilities for domain-based tests."""

import inspect
from typing import Any

import msgspec
from litestar.testing import AsyncTestClient

from app.actions.registry import ActionRegistry
from app.actions.schemas import build_action_union

# Build the Action union type from all registered actions
Action = build_action_union(ActionRegistry())


async def get_available_actions(
    client: AsyncTestClient,
    action_group: str,
    obj_id: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch available actions for an object or action group.

    Args:
        client: Authenticated test client
        action_group: Action group name (e.g., "brand_actions", "roster_actions")
        obj_id: Optional SQID-encoded object ID for object-specific actions

    Returns:
        List of available action metadata dicts
    """
    url = f"/actions/{action_group}"
    if obj_id is not None:
        url = f"{url}/{obj_id}"

    response = await client.get(url)
    assert response.status_code == 200, f"Failed to fetch actions: {response.text}"
    data = response.json()

    # Handle different response formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "actions" in data:
        return data["actions"]
    else:
        # Fallback: return empty list if unexpected format
        return []


async def execute_action(
    client: AsyncTestClient,
    action_group: str,
    action_key: str,
    data: dict[str, Any] | None = None,
    obj_id: str | None = None,
) -> Any:
    """Execute an action and return the response.

    Args:
        client: Authenticated test client
        action_group: Action group name (e.g., "brand_actions", "roster_actions")
        action_key: Action key (e.g., "brand_actions__brand_update")
        data: Optional data payload for the action
        obj_id: Optional SQID-encoded object ID for object-specific actions

    Returns:
        Response object from the action execution
    """
    url = f"/actions/{action_group}"
    if obj_id is not None:
        url = f"{url}/{obj_id}"

    # Build the action payload using msgspec
    payload_dict: dict[str, Any] = {"action": action_key}
    if data is not None:
        payload_dict["data"] = data

    # Encode to JSON using msgspec for proper serialization
    json_bytes = msgspec.json.encode(payload_dict)

    response = await client.post(url, content=json_bytes, headers={"Content-Type": "application/json"})
    return response


def generate_minimal_action_data(action_class: type) -> dict[str, Any]:
    """Generate minimal valid data for an action based on its execute method signature.

    Args:
        action_class: Action class with execute() method

    Returns:
        Dict with minimal valid data for the action
    """
    # Get execute method signature
    execute_method = getattr(action_class, "execute", None)
    if not execute_method:
        return {}

    sig = inspect.signature(execute_method)

    # Look for 'data' parameter
    if "data" not in sig.parameters:
        return {}

    # Get the data parameter type
    data_param = sig.parameters["data"]
    data_type = data_param.annotation

    # If no type annotation, return empty dict
    if data_type == inspect.Parameter.empty:
        return {}

    # For msgspec structs, try to instantiate with defaults
    # This is a simplified approach - in practice, you might need to handle
    # different types more carefully
    try:
        # Try to get the struct's fields and create minimal data
        if hasattr(data_type, "__annotations__"):
            minimal_data = {}
            for field_name, field_type in data_type.__annotations__.items():
                # Generate minimal valid values based on type
                if field_type == str or field_type == str | None:
                    minimal_data[field_name] = "test"
                elif field_type == int or field_type == int | None:
                    minimal_data[field_name] = 1
                elif field_type == bool or field_type == bool | None:
                    minimal_data[field_name] = True
                # Add more type handlers as needed
            return minimal_data
    except Exception:
        # If we can't introspect, return empty dict
        return {}

    return {}


async def verify_all_actions_for_group(
    client: AsyncTestClient,
    action_group: str,
    test_object: Any,
    custom_data: dict[str, dict[str, Any]] | None = None,
) -> None:
    """Verify all available actions for an action group can execute.

    This helper tests that all actions for a given object can execute without errors.

    Args:
        client: Authenticated test client
        action_group: Action group name (e.g., "brands")
        test_object: Object instance to test actions on
        custom_data: Optional dict mapping action_key -> data payload
    """
    # Get available actions
    actions = await get_available_actions(client, action_group, test_object.id)

    for action in actions:
        action_key = action["key"]

        # Get custom data or empty dict
        data = (custom_data or {}).get(action_key, {})

        # Execute action
        response = await execute_action(client, action_group, action_key, data, test_object.id)

        # Assert success (200, 201, 204 are all valid success codes)
        assert response.status_code in [
            200,
            201,
            204,
        ], f"Action {action_key} failed with status {response.status_code}: {response.text}"
