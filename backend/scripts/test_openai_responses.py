#!/usr/bin/env python3
"""Test OpenAI Responses API with local PDF file.

Usage:
    uv run python scripts/test_openai_responses.py <pdf_path>

Example:
    uv run python scripts/test_openai_responses.py ~/Downloads/contract.pdf
"""

import asyncio
import io
import json
import logging
import os
import sys
from pathlib import Path

import msgspec
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables from backend/.env.local
env_path = Path(__file__).parent.parent / ".env.local"
load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# Simple test schema
class SimpleExtractionSchema(msgspec.Struct):
    """Simple schema for testing."""

    campaign_name: str
    company_name: str | None = None
    total_amount: float | None = None
    notes: str | None = None


async def test_openai_responses_api(pdf_path: str) -> None:
    """Test OpenAI Responses API with a local PDF file."""
    # Check file exists
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        logger.error(f"File not found: {pdf_path}")
        sys.exit(1)

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=api_key)

    try:
        # Step 1: Upload file to OpenAI
        logger.info(f"Uploading file: {pdf_file.name}")
        with open(pdf_file, "rb") as f:
            file_bytes = f.read()

        file_obj = io.BytesIO(file_bytes)
        file_obj.name = pdf_file.name

        file_response = await client.files.create(file=file_obj, purpose="assistants")
        file_id = file_response.id
        logger.info(f"File uploaded: {file_id}")

        # Step 2: Generate JSON schema
        schema_dict = msgspec.json.schema(SimpleExtractionSchema)

        # Extract the actual schema from $ref if present
        if "$ref" in schema_dict and "$defs" in schema_dict:
            # Get the schema name from $ref (e.g., "#/$defs/SimpleExtractionSchema" -> "SimpleExtractionSchema")
            ref_name = schema_dict["$ref"].split("/")[-1]
            # Use the actual schema definition
            actual_schema = schema_dict["$defs"][ref_name]
            logger.info(f"Extracted schema from $ref: {json.dumps(actual_schema, indent=2)}")
        else:
            actual_schema = schema_dict
            logger.info(f"Generated schema: {json.dumps(actual_schema, indent=2)}")

        # OpenAI strict mode requires:
        # 1. additionalProperties: false
        # 2. All properties must be in required array
        actual_schema["additionalProperties"] = False
        if "properties" in actual_schema:
            actual_schema["required"] = list(actual_schema["properties"].keys())

        # Step 3: Call Responses API with file attachment
        logger.info("Calling OpenAI Responses API...")

        instructions = """
Extract the following information from this contract PDF:
- campaign_name: The name or title of the campaign/project
- company_name: The company or brand name
- total_amount: Total compensation amount in USD (number only)
- notes: Any important notes or observations

Return only valid JSON.
"""

        response = await client.responses.create(  # type: ignore
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "file_id": file_id,
                        },
                        {
                            "type": "input_text",
                            "text": instructions,
                        },
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "SimpleExtractionSchema",
                    "strict": True,
                    "schema": actual_schema,
                }
            },
            temperature=0.1,
        )

        # Step 4: Parse response
        logger.info(f"Response received. ID: {response.id}")
        logger.info(f"Response output type: {type(response.output)}")
        logger.info(f"Response output length: {len(response.output) if response.output else 0}")

        if not response.output:
            logger.error("Empty output from OpenAI response")
            sys.exit(1)

        # Debug: Print raw output structure
        logger.info("=" * 80)
        logger.info("RAW RESPONSE STRUCTURE:")
        logger.info("=" * 80)
        for i, item in enumerate(response.output):
            logger.info(f"\nOutput item {i}:")
            logger.info(f"  Type: {item.type}")
            logger.info(f"  Has content attr: {hasattr(item, 'content')}")
            if hasattr(item, "content"):
                logger.info(f"  Content type: {type(item.content)}")  # type: ignore
                logger.info(f"  Content length: {len(item.content) if item.content else 0}")  # type: ignore

                if item.content:  # type: ignore
                    for j, content_block in enumerate(item.content):  # type: ignore
                        logger.info(f"\n  Content block {j}:")
                        logger.info(f"    Block type: {content_block.type}")
                        logger.info(f"    Block attributes: {dir(content_block)}")

                        if content_block.type == "output_text":
                            logger.info(
                                f"    Text preview: {content_block.text[:200] if hasattr(content_block, 'text') else 'NO TEXT ATTR'}"  # type: ignore
                            )

        # Extract structured output
        logger.info("\n" + "=" * 80)
        logger.info("ATTEMPTING EXTRACTION:")
        logger.info("=" * 80)

        result = None
        for item in response.output:
            if item.type == "message" and hasattr(item, "content"):
                for content_block in item.content:  # type: ignore
                    if content_block.type == "output_text":
                        # Parse JSON and validate with msgspec
                        json_text = content_block.text  # type: ignore
                        logger.info(f"\nFound output_text: {json_text}")

                        json_bytes = json_text.encode("utf-8")
                        result = msgspec.json.decode(json_bytes, type=SimpleExtractionSchema)
                        break
                if result:
                    break

        if not result:
            logger.error("No structured output found in response")
            sys.exit(1)

        # Step 5: Display results
        logger.info("\n" + "=" * 80)
        logger.info("EXTRACTION RESULTS:")
        logger.info("=" * 80)
        logger.info(f"Campaign Name: {result.campaign_name}")
        logger.info(f"Company Name: {result.company_name}")
        logger.info(f"Total Amount: ${result.total_amount:,.2f}" if result.total_amount else "Total Amount: N/A")
        logger.info(f"Notes: {result.notes}")
        logger.info("=" * 80)

        # Step 6: Cleanup - delete file
        logger.info(f"\nDeleting file: {file_id}")
        await client.files.delete(file_id)
        logger.info("✓ Test completed successfully!")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)

        # Try to cleanup file on error
        try:
            if "file_id" in locals():
                await client.files.delete(file_id)
                logger.info(f"Cleaned up file: {file_id}")
        except Exception:
            pass

        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/test_openai_responses.py <pdf_path>")
        print("\nExample:")
        print("  uv run python scripts/test_openai_responses.py ~/Downloads/contract.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    asyncio.run(test_openai_responses_api(pdf_path))
