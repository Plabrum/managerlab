#!/usr/bin/env python3
"""Test script to see raw msgspec schema output."""

import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import msgspec

from app.agents.schemas import CampaignExtractionSchema


def main():
    """Test msgspec raw schema generation."""
    print("Raw msgspec schema:")
    print("=" * 80)

    # Generate raw schema
    schema = msgspec.json.schema(CampaignExtractionSchema)

    # Pretty print
    print(json.dumps(schema, indent=2))


if __name__ == "__main__":
    main()
