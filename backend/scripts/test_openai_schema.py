#!/usr/bin/env python3
"""Test script to verify OpenAI schema conversion works correctly."""

import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.agents.schemas import CampaignExtractionSchema
from app.utils.openai_schema import to_openai_json_schema


def main():
    """Test schema conversion and verify no $ref or $defs remain."""
    print("Testing OpenAI schema conversion...")
    print("=" * 80)

    # Convert schema
    schema = to_openai_json_schema(CampaignExtractionSchema)

    # Pretty print the schema
    print("\nGenerated Schema:")
    print("-" * 80)
    print(json.dumps(schema, indent=2))
    print("-" * 80)

    # Check for problematic patterns
    schema_str = json.dumps(schema)

    issues = []

    if "$ref" in schema_str:
        issues.append("❌ Schema contains $ref references")
    else:
        print("✅ No $ref references found")

    if "$defs" in schema_str:
        issues.append("❌ Schema contains $defs")
    else:
        print("✅ No $defs found")

    if "definitions" in schema_str:
        issues.append("❌ Schema contains definitions")
    else:
        print("✅ No definitions found")

    # Check that CounterpartyType enum is inlined
    if "counterparty_type" in schema_str:
        print("✅ counterparty_type field exists")
        # Find the counterparty_type property in the schema
        if "properties" in schema and "counterparty_type" in schema["properties"]:
            ct_schema = schema["properties"]["counterparty_type"]
            print(f"   counterparty_type schema: {json.dumps(ct_schema, indent=4)}")
            if "enum" in str(ct_schema):
                print("✅ counterparty_type has enum values inlined")
            else:
                issues.append("❌ counterparty_type missing enum values")
        else:
            issues.append("❌ counterparty_type not in properties")

    print("\n" + "=" * 80)
    if issues:
        print("FAILED - Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return 1
    else:
        print("SUCCESS - Schema is valid for OpenAI Responses API!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
