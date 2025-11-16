"""Campaign Contract Decoder Agent - Extracts structured campaign data from contract documents."""

import json
import logging
from typing import Any

import msgspec

from app.agents.schemas import CampaignExtractionSchema
from app.client.openai_client import BaseOpenAIClient

logger = logging.getLogger(__name__)


class CampaignDecoderAgent:
    """
    OpenAI agent for extracting structured campaign data from contract documents.

    This agent processes contract PDFs/documents and returns structured data
    matching the CampaignExtractionSchema format.
    """

    instructions = """You are a Campaign Contract Decoder Agent. Your task is to extract structured campaign data from the provided contract document.

**EXTRACTION GUIDELINES:**

1. **Campaign Basics:**
   - Extract campaign name (look for "Campaign Name", "Project Name", or infer from context)
   - Extract description/overview if present

2. **Counterparty Information:**
   - Identify if counterparty is "AGENCY" or "BRAND" (default: BRAND)
   - Extract company/brand name
   - Extract contact email if available

3. **Compensation Structure:**
   - Identify structure type: "FLAT_FEE", "PER_DELIVERABLE", or "PERFORMANCE_BASED"
   - Extract total compensation in USD
   - Extract payment terms (e.g., NET-30 = 30 days)
   - Extract payment schedule/milestones with:
     * Label (e.g., "Upfront", "Upon Delivery")
     * Trigger condition
     * Amount in USD or percentage
     * NET payment terms in days

4. **Flight Dates:**
   - Start date (campaign/content goes live)
   - End date (campaign ends)
   - Format: YYYY-MM-DD

5. **FTC & Usage Rights:**
   - FTC disclosure string (e.g., "#ad #sponsored")
   - Usage duration (in days or description like "Perpetual", "12 months")
   - Usage territory (e.g., "Worldwide", "USA only")
   - Paid media option (true/false - can brand use in paid ads?)

6. **Exclusivity:**
   - Category (e.g., "Beauty", "Fashion", "All Categories")
   - Days before campaign (blackout period before)
   - Days after campaign (blackout period after)

7. **Content Ownership:**
   - Ownership mode: "BRAND_OWNED", "CREATOR_OWNED", or "SHARED"

8. **Approval Process:**
   - Number of approval rounds
   - SLA in hours for each approval

**OUTPUT FORMAT:**

Return valid JSON matching this schema:
- All fields are optional except "name"
- Use null for missing/unclear fields
- Dates in ISO format (YYYY-MM-DD)
- Numbers as integers or floats (not strings)
- Enums must match exactly: "FLAT_FEE", "PER_DELIVERABLE", "PERFORMANCE_BASED", "AGENCY", "BRAND", "BRAND_OWNED", "CREATOR_OWNED", "SHARED"

**CONFIDENCE & NOTES:**

- Include a confidence_score (0.0 to 1.0) indicating extraction confidence
- Add extraction_notes for any ambiguities, assumptions, or missing information

**EXAMPLE OUTPUT:**

{
  "name": "Summer Beauty Campaign 2025",
  "description": "Influencer partnership for new skincare line launch",
  "counterparty_type": "BRAND",
  "counterparty_name": "Glow Beauty Inc.",
  "counterparty_email": "partnerships@glowbeauty.com",
  "compensation_structure": "FLAT_FEE",
  "compensation_total_usd": 10000.0,
  "payment_terms_days": 30,
  "payment_blocks": [
    {
      "label": "Signing Bonus",
      "trigger": "Upon contract execution",
      "amount_usd": 5000.0,
      "net_days": 0
    },
    {
      "label": "Delivery Payment",
      "trigger": "Upon content approval",
      "amount_usd": 5000.0,
      "net_days": 30
    }
  ],
  "flight_start_date": "2025-06-01",
  "flight_end_date": "2025-08-31",
  "ftc_string": "#ad #GlowPartner",
  "usage_duration": "365",
  "usage_territory": "United States",
  "usage_paid_media_option": true,
  "exclusivity_category": "Skincare",
  "exclusivity_days_before": 30,
  "exclusivity_days_after": 60,
  "ownership_mode": "BRAND_OWNED",
  "approval_rounds": 2,
  "approval_sla_hours": 48,
  "confidence_score": 0.92,
  "extraction_notes": "Payment schedule clearly defined. Exclusivity applies to skincare category only."
}

Extract all available information from the document. Be thorough but accurate."""

    @staticmethod
    def _msgspec_to_json_schema(schema_class: type[msgspec.Struct]) -> dict[str, Any]:
        """
        Convert msgspec Struct to JSON Schema dict for OpenAI structured outputs.

        Args:
            schema_class: msgspec.Struct class

        Returns:
            JSON Schema dictionary
        """
        # Get msgspec schema info
        schema_info = msgspec.json.schema(schema_class)

        # OpenAI expects a specific format
        # We need to ensure the schema has the right structure
        return {
            "type": "object",
            "properties": schema_info.get("properties", {}),
            "required": schema_info.get("required", []),
            "additionalProperties": False,
        }

    @staticmethod
    def _parse_extraction_result(result_dict: dict[str, Any]) -> CampaignExtractionSchema:
        """
        Parse OpenAI extraction result into msgspec schema.

        Args:
            result_dict: Raw dictionary from OpenAI response

        Returns:
            Validated CampaignExtractionSchema instance

        Raises:
            msgspec.ValidationError: If response doesn't match schema
        """
        # Serialize to JSON then deserialize with msgspec for validation
        json_bytes = msgspec.json.encode(result_dict)
        return msgspec.json.decode(json_bytes, type=CampaignExtractionSchema)

    async def run(
        self,
        file_bytes: bytes,
        filename: str,
        openai_client: BaseOpenAIClient,
    ) -> CampaignExtractionSchema:
        """
        Execute the campaign decoder agent.

        Args:
            file_bytes: Contract document file bytes
            filename: Original filename (for context and content type)
            openai_client: OpenAI client instance

        Returns:
            CampaignExtractionSchema with extracted data

        Raises:
            Exception: On extraction or parsing failure
        """
        file_id = None

        try:
            # Step 1: Upload file to OpenAI
            logger.info(f"Starting campaign extraction for file: {filename}")
            file_obj = await openai_client.upload_file(file_bytes, filename, purpose="assistants")
            file_id = file_obj.id

            # Step 2: Generate JSON schema from msgspec
            json_schema = self._msgspec_to_json_schema(CampaignExtractionSchema)

            # Step 3: Run structured extraction
            result_dict = await openai_client.run_structured_extraction(
                file_id=file_id,
                instructions=self.instructions,
                schema_dict=json_schema,
            )

            # Step 4: Parse and validate result
            extraction_result = self._parse_extraction_result(result_dict)

            logger.info(
                f"Campaign extraction completed successfully: {extraction_result.name} "
                f"(confidence: {extraction_result.confidence_score})"
            )

            return extraction_result

        except Exception as e:
            logger.error(f"Campaign extraction failed for {filename}: {e}")
            raise

        finally:
            # Step 5: Clean up - delete file from OpenAI (immediate deletion strategy)
            if file_id:
                try:
                    await openai_client.delete_file(file_id)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up OpenAI file {file_id}: {cleanup_error}")


# Global singleton instance
campaign_decoder_agent = CampaignDecoderAgent()
