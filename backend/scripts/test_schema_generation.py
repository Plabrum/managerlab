#!/usr/bin/env python3
"""Test schema generation for CampaignExtractionSchema."""

import json
import sys
from pathlib import Path

import msgspec

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.schemas import CampaignExtractionSchema


def test_schema_generation():
    """Test that we generate valid schema with all nested types."""
    # Generate JSON schema from msgspec type
    schema_dict = msgspec.json.schema(CampaignExtractionSchema)

    print("=" * 80)
    print("RAW SCHEMA FROM MSGSPEC:")
    print("=" * 80)
    print(json.dumps(schema_dict, indent=2))
    print()

    # Extract actual schema if it uses $ref (msgspec wraps schemas in $ref/$defs)
    if "$ref" in schema_dict and "$defs" in schema_dict:
        ref_name = schema_dict["$ref"].split("/")[-1]
        actual_schema = schema_dict["$defs"][ref_name].copy()
        # Include all $defs from the original schema (for nested types)
        if "$defs" in schema_dict:
            actual_schema["$defs"] = schema_dict["$defs"]
    else:
        actual_schema = schema_dict

    print("=" * 80)
    print("EXTRACTED SCHEMA WITH $DEFS:")
    print("=" * 80)
    print(json.dumps(actual_schema, indent=2))
    print()

    # OpenAI strict mode requires:
    # 1. additionalProperties: false on the root and all nested objects
    # 2. All properties must be in required array
    def add_strict_requirements(obj: dict) -> None:
        """Recursively add strict mode requirements to schema."""
        if isinstance(obj, dict):
            if obj.get("type") == "object":
                obj["additionalProperties"] = False
                if "properties" in obj:
                    obj["required"] = list(obj["properties"].keys())
            # Recurse into nested structures
            for value in obj.values():
                if isinstance(value, dict):
                    add_strict_requirements(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            add_strict_requirements(item)

    add_strict_requirements(actual_schema)

    print("=" * 80)
    print("FINAL SCHEMA WITH STRICT REQUIREMENTS:")
    print("=" * 80)
    print(json.dumps(actual_schema, indent=2))
    print()

    # Check if all referenced types are in $defs
    if "$defs" in actual_schema:
        print("=" * 80)
        print("AVAILABLE TYPES IN $DEFS:")
        print("=" * 80)
        for def_name in actual_schema["$defs"].keys():
            print(f"  - {def_name}")
        print()

    print("✓ Schema generation test completed!")


if __name__ == "__main__":
    test_schema_generation()
