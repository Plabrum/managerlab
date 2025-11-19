#!/usr/bin/env python3
"""Direct test of OpenAI structured extraction with the real PDF - no S3 needed."""

import asyncio
import io
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from openai import AsyncOpenAI

from app.agents.schemas import CampaignExtractionSchema
from app.utils.configure import get_config
from app.utils.openai_schema import parse_structured_response, to_openai_json_schema


async def main():
    """Test OpenAI extraction with the actual PDF - direct API call."""
    print("Testing OpenAI Structured Extraction (Direct)")
    print("=" * 80)

    # Get config
    config = get_config()

    if not config.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set in environment")
        return 1

    # Initialize OpenAI client
    client = AsyncOpenAI(
        api_key=config.OPENAI_API_KEY, organization=config.OPENAI_ORG_ID if hasattr(config, "OPENAI_ORG_ID") else None
    )

    # Load the PDF
    pdf_path = Path.home() / "Desktop" / "Henry Farrell x Cantina Chicken Menu agreement 10.15.pdf"

    if not pdf_path.exists():
        print(f"❌ PDF not found at: {pdf_path}")
        return 1

    print(f"Found PDF at: {pdf_path}")
    print(f"File size: {pdf_path.stat().st_size / 1024:.2f} KB")

    try:
        # Step 1: Upload file to OpenAI
        print("\nStep 1: Uploading PDF to OpenAI...")
        with open(pdf_path, "rb") as f:
            file_obj = await client.files.create(file=f, purpose="assistants")

        print(f"✅ File uploaded: {file_obj.id}")

        # Step 2: Generate schema
        print("\nStep 2: Converting msgspec schema to OpenAI format...")
        openai_schema = to_openai_json_schema(CampaignExtractionSchema)
        print(f"✅ Schema generated ({len(str(openai_schema))} chars)")

        # Step 3: Call Responses API
        print("\nStep 3: Calling OpenAI Responses API...")
        instructions = """Extract campaign information from this contract."""

        response = await client.responses.create(  # type: ignore
            model=config.OPENAI_MODEL if hasattr(config, "OPENAI_MODEL") else "gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "file_id": file_obj.id,
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
                    "name": "CampaignExtractionSchema",
                    "strict": True,
                    "schema": openai_schema,
                }
            },
            temperature=0.1,
        )

        print("✅ API call successful")

        # Step 4: Parse response
        print("\nStep 4: Parsing structured response...")
        result = parse_structured_response(response, CampaignExtractionSchema)

        print("\n✅ EXTRACTION SUCCESSFUL!")
        print("=" * 80)
        print(f"Campaign Name: {result.name}")
        print(f"Description: {result.description}")
        print(f"Counterparty: {result.counterparty_name} ({result.counterparty_type})")
        print(f"Compensation: ${result.compensation_total_usd} ({result.compensation_structure})")
        print(f"Flight: {result.flight_start_date} to {result.flight_end_date}")
        print(f"Payment Blocks: {len(result.payment_blocks)}")
        for i, block in enumerate(result.payment_blocks, 1):
            print(f"  Block {i}: {block.label} - ${block.amount_usd} ({block.percent}%)")
        print(f"Confidence Score: {result.confidence_score}")
        if result.extraction_notes:
            print(f"Notes: {result.extraction_notes}")
        print("=" * 80)

        # Step 5: Cleanup
        print("\nStep 5: Cleaning up file from OpenAI...")
        await client.files.delete(file_obj.id)
        print("✅ File deleted")

        return 0

    except Exception as e:
        print(f"\n❌ EXTRACTION FAILED!")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print("\nFull traceback:")
        import traceback

        traceback.print_exc()
        print("=" * 80)

        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
