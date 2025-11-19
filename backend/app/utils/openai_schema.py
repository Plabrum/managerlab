"""Utilities for working with OpenAI's Responses API and structured outputs.

OpenAI's structured outputs (strict mode) have specific requirements:
1. No unsupported JSON Schema keywords (like $schema, title, etc.)
2. No union types (anyOf, oneOf, allOf)
3. All objects must have "additionalProperties": false
4. All object properties must be listed in "required"

This module provides utilities to:
- Convert msgspec schemas to OpenAI-compatible format
- Parse structured responses from the Responses API
"""

import logging
from typing import TypeVar

import msgspec

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=msgspec.Struct)

# Keywords that OpenAI's strict mode doesn't support
UNSUPPORTED_KEYS = {
    "$schema",
    "title",
    "description",
    "$defs",
    "definitions",
    "examples",
    "default",
    "nullable",
}


def to_openai_json_schema(type_: type) -> dict:
    """
    Convert a msgspec Struct to an OpenAI-safe JSON Schema.

    This function:
    1. Generates a JSON schema from the msgspec type
    2. Inlines the root schema definition (removes $ref wrapper)
    3. Strips unsupported keywords
    4. Resolves union types (anyOf/oneOf) to their first alternative
    5. Adds strict mode requirements (additionalProperties, required)

    Args:
        type_: A msgspec.Struct type to generate schema for

    Returns:
        dict: OpenAI-compatible JSON schema

    Example:
        >>> from msgspec import Struct
        >>> class User(Struct):
        ...     name: str
        ...     age: int
        >>> schema = to_openai_json_schema(User)
    """
    # Generate full JSON schema from msgspec
    full_schema = msgspec.json.schema(type_)

    # msgspec puts the actual schema under "$defs" with a "$ref" at the root
    # We need to inline the referenced definition
    if "$ref" in full_schema:
        ref_name = full_schema["$ref"].split("/")[-1]
        defs = full_schema.get("$defs", {})
        root = defs.get(ref_name)
        if root is None:
            logger.warning(f"Referenced schema '{ref_name}' not found in $defs")
            root = full_schema
    else:
        root = full_schema

    # Strip unsupported keys and resolve unions
    clean = _strip_unsupported(root)

    # Add OpenAI strict mode requirements
    if isinstance(clean, dict):
        _add_strict_requirements(clean)
        return clean
    else:
        # Should not happen if root is a valid schema, but handle it
        logger.warning(f"Unexpected schema type after stripping: {type(clean)}")
        return {} if not isinstance(clean, dict) else clean


def _strip_unsupported(value) -> dict | list | str | int | float | bool | None:  # type: ignore
    """
    Recursively remove unsupported keys and resolve nested schemas.

    OpenAI's strict mode doesn't support:
    - Union types (anyOf, oneOf, allOf) - we take the first alternative
    - Various metadata keys ($schema, title, description, etc.)

    Args:
        value: The schema value to process (dict, list, or primitive)

    Returns:
        Processed value with unsupported features removed
    """
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            # Drop keys OpenAI doesn't support
            if k in UNSUPPORTED_KEYS:
                continue

            # Handle union types (anyOf, oneOf, allOf)
            # OpenAI doesn't support unions, so we take the first non-null alternative
            if k in ("oneOf", "anyOf", "allOf"):
                # Find first alternative that isn't just {"type": "null"}
                for alternative in v:
                    if isinstance(alternative, dict) and alternative.get("type") != "null":
                        v = alternative
                        break
                else:
                    # All alternatives were null or we couldn't find a good one
                    # Just take the first one
                    v = v[0] if v else {}

                # The union key itself is removed, we inline the chosen alternative
                stripped = _strip_unsupported(v)
                if isinstance(stripped, dict):
                    out.update(stripped)
                continue

            out[k] = _strip_unsupported(v)
        return out

    elif isinstance(value, list):
        return [_strip_unsupported(v) for v in value]

    else:
        return value


def _add_strict_requirements(schema: dict) -> None:
    """
    Recursively add OpenAI strict mode requirements to a JSON schema.

    OpenAI's strict mode enforces that:
    1. All objects must set "additionalProperties": false
    2. All object properties must be listed in "required"

    This modifies the schema in-place.

    Args:
        schema: The JSON schema to modify
    """
    if not isinstance(schema, dict):
        return

    # Add strict requirements to object types
    if schema.get("type") == "object":
        schema["additionalProperties"] = False
        if "properties" in schema:
            # All properties must be required in strict mode
            schema["required"] = list(schema["properties"].keys())

    # Recursively process all nested structures
    for value in schema.values():
        if isinstance(value, dict):
            _add_strict_requirements(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _add_strict_requirements(item)


def parse_structured_response(response, schema_type: type[T]) -> T:
    """
    Parse structured output from an OpenAI Responses API response.

    The Responses API returns output as a list of items, where each item
    can be a message, tool call, etc. For structured outputs, we expect
    a message with output_text content containing the JSON.

    Args:
        response: The response object from client.responses.create()
        schema_type: The msgspec.Struct type to decode the JSON into

    Returns:
        Parsed and validated instance of schema_type

    Raises:
        ValueError: If the response doesn't contain expected structured output

    Example:
        >>> response = await client.responses.create(...)
        >>> result = parse_structured_response(response, CampaignExtractionSchema)
    """
    if not response.output:
        raise ValueError("Empty output from OpenAI response")

    # Find the first message with output_text
    for item in response.output:
        if item.type != "message":
            continue

        if not hasattr(item, "content") or not item.content:
            continue

        # Look for output_text content block
        for content_block in item.content:  # type: ignore
            if content_block.type == "output_text":
                # Parse and validate JSON with msgspec
                json_text = content_block.text  # type: ignore
                json_bytes = json_text.encode("utf-8")
                result = msgspec.json.decode(json_bytes, type=schema_type)

                logger.info(f"Parsed structured output: {type(result).__name__}")
                return result

    # If we get here, we didn't find any output_text
    raise ValueError(
        f"No output_text found in OpenAI response. "
        f"Response had {len(response.output)} output items. "
        f"Types: {[item.type for item in response.output]}"
    )
