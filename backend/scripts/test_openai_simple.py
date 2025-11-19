#!/usr/bin/env python3
"""Minimal test of OpenAI Responses API without files.

This tests the basic Responses API functionality without file uploads.

Usage:
    uv run python scripts/test_openai_simple.py
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

import msgspec
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env.local")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class SimpleSchema(msgspec.Struct):
    """Simple test schema."""

    summary: str
    number: int | None = None


async def test_responses_api() -> None:
    """Test basic Responses API call."""
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        logger.error("Please set it:")
        logger.error("  export OPENAI_API_KEY='your-api-key'")
        logger.error("Or add it to backend/.env.local:")
        logger.error("  OPENAI_API_KEY=your-api-key")
        sys.exit(1)

    client = AsyncOpenAI(api_key=api_key)

    try:
        # Generate schema
        schema_dict = msgspec.json.schema(SimpleSchema)
        logger.info(f"Schema: {json.dumps(schema_dict, indent=2)}")

        # Test 1: Simple text input
        logger.info("\n" + "=" * 80)
        logger.info("TEST 1: Simple text input")
        logger.info("=" * 80)

        response = await client.responses.create(  # type: ignore
            model="gpt-4o",
            input="Summarize this: The weather is nice today. There are 5 clouds.",
            text={
                "format": {
                    "type": "json_schema",
                    "name": "SimpleSchema",
                    "strict": True,
                    "schema": schema_dict,
                }
            },
        )

        logger.info(f"Response ID: {response.id}")
        logger.info(f"Output items: {len(response.output) if response.output else 0}")

        # Parse output
        for item in response.output:
            logger.info(f"Item type: {item.type}")
            if item.type == "message" and hasattr(item, "content"):
                for block in item.content:  # type: ignore
                    logger.info(f"  Block type: {block.type}")
                    if block.type == "output_text":
                        json_text = block.text  # type: ignore
                        logger.info(f"  Text: {json_text}")

                        result = msgspec.json.decode(json_text.encode(), type=SimpleSchema)
                        logger.info(f"\n✓ Parsed result:")
                        logger.info(f"  Summary: {result.summary}")
                        logger.info(f"  Number: {result.number}")

        # Test 2: Array input format (like we use for files)
        logger.info("\n" + "=" * 80)
        logger.info("TEST 2: Array input format (mimics file attachment structure)")
        logger.info("=" * 80)

        response2 = await client.responses.create(  # type: ignore
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Summarize this: It's raining. I see 10 raindrops.",
                        },
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "SimpleSchema",
                    "strict": True,
                    "schema": schema_dict,
                }
            },
        )

        logger.info(f"Response ID: {response2.id}")
        logger.info(f"Output items: {len(response2.output) if response2.output else 0}")

        for item in response2.output:
            logger.info(f"Item type: {item.type}")
            if item.type == "message" and hasattr(item, "content"):
                for block in item.content:  # type: ignore
                    logger.info(f"  Block type: {block.type}")
                    if block.type == "output_text":
                        json_text = block.text  # type: ignore
                        logger.info(f"  Text: {json_text}")

                        result = msgspec.json.decode(json_text.encode(), type=SimpleSchema)
                        logger.info(f"\n✓ Parsed result:")
                        logger.info(f"  Summary: {result.summary}")
                        logger.info(f"  Number: {result.number}")

        logger.info("\n" + "=" * 80)
        logger.info("✓ All tests passed!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_responses_api())
