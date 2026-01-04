#!/usr/bin/env python3
"""Test script for campaign extraction from PDF attachments.

Usage:
    uv run python scripts/test_campaign_extraction.py <s3_key>

Example:
    uv run python scripts/test_campaign_extraction.py inbound-emails/attachments/test.pdf
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.campaign_decoder import CampaignDecoderAgent
from app.client.openai_client import OpenAIClient
from app.client.s3_client import S3Client
from app.utils.configure import get_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_extraction(s3_key: str) -> None:
    """Test campaign extraction from S3 file."""
    config = get_config()

    # Initialize clients
    s3_client = S3Client(config=config)

    openai_client = OpenAIClient(
        api_key=config.OPENAI_API_KEY,
        s3_client=s3_client,
        organization=config.OPENAI_ORG_ID,
        model=config.OPENAI_MODEL,
    )

    # Run extraction
    logger.info(f"Starting extraction for S3 key: {s3_key}")
    agent = CampaignDecoderAgent(openai_client)

    try:
        result = await agent.run(s3_key=s3_key)

        # Print results
        print("\n" + "=" * 80)
        print("EXTRACTION RESULTS")
        print("=" * 80)

        # Convert to dict for pretty printing
        result_dict = {
            "name": result.name,
            "description": result.description,
            "counterparty_name": result.counterparty_name,
            "counterparty_email": result.counterparty_email,
            "counterparty_type": result.counterparty_type,
            "compensation_structure": result.compensation_structure,
            "compensation_total_usd": result.compensation_total_usd,
            "payment_terms_days": result.payment_terms_days,
            "payment_blocks": [
                {
                    "label": pb.label,
                    "trigger": pb.trigger,
                    "amount_usd": pb.amount_usd,
                    "percent": pb.percent,
                    "net_days": pb.net_days,
                }
                for pb in result.payment_blocks
            ],
            "flight_start_date": result.flight_start_date.isoformat() if result.flight_start_date else None,
            "flight_end_date": result.flight_end_date.isoformat() if result.flight_end_date else None,
            "ftc_string": result.ftc_string,
            "usage_duration": result.usage_duration,
            "usage_territory": result.usage_territory,
            "usage_paid_media_option": result.usage_paid_media_option,
            "exclusivity_category": result.exclusivity_category,
            "exclusivity_days_before": result.exclusivity_days_before,
            "exclusivity_days_after": result.exclusivity_days_after,
            "ownership_mode": result.ownership_mode,
            "approval_rounds": result.approval_rounds,
            "approval_sla_hours": result.approval_sla_hours,
            "confidence_score": result.confidence_score,
            "extraction_notes": result.extraction_notes,
        }

        print(json.dumps(result_dict, indent=2, default=str))
        print("\n" + "=" * 80)
        print("✓ Extraction completed successfully!")
        print(f"  Campaign: {result.name}")
        print(f"  Counterparty: {result.counterparty_name}")
        print(f"  Confidence: {result.confidence_score}")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/test_campaign_extraction.py <s3_key>")
        print("\nExample:")
        print("  uv run python scripts/test_campaign_extraction.py inbound-emails/attachments/test.pdf")
        sys.exit(1)

    s3_key = sys.argv[1]
    asyncio.run(test_extraction(s3_key))
