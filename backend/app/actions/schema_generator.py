"""Dynamic schema generation for action data based on execute method signatures."""

import inspect
from typing import Any, Union

from msgspec import defstruct

from app.actions.registry import ActionRegistry
from app.base.schemas import BaseSchema


def extract_data_type(action_class: type) -> type:
    """Extract data type from action's execute method signature.

    Unwraps DTOData[Model] to Model for OpenAPI schema generation.
    """
    sig = inspect.signature(action_class.execute)

    if "data" not in sig.parameters:
        return dict[str, Any]

    annotation = sig.parameters["data"].annotation
    if annotation is inspect.Parameter.empty:
        return dict[str, Any]

    return annotation


def generate_all_action_schemas() -> BaseSchema:
    """Generate discriminated union of action schemas from registered actions."""
    registry = ActionRegistry()

    if not registry._flat_registry:
        raise RuntimeError("No actions registered - cannot generate schemas")

    schemas = []

    for combined_key, action_class in registry._flat_registry.items():
        data_type = extract_data_type(action_class)
        class_name = (
            f"{''.join(w.capitalize() for w in combined_key.split('_'))}ActionData"
        )

        # Create tagged struct - tag_field="action", tag=combined_key
        # msgspec auto-adds the 'action' field with the tag value
        schema_class = defstruct(
            class_name,
            [("data", data_type)],
            tag_field="action",
            tag=combined_key,
        )
        schemas.append(schema_class)

    return Union[tuple(schemas)]  # type: ignore
