"""Schemas for AI agent extraction outputs.

These schemas inherit from base field schemas defined in domain modules to ensure
they stay in sync with the actual model fields. When a field is added to a model,
it should be added to the corresponding base schema in the domain module
(campaigns/schemas.py or deliverables/schemas.py), which will automatically
propagate to both create and extraction schemas.
"""

from app.base.schemas import BaseSchema

# Import base field schemas from domain modules
# This ensures extraction schemas stay in sync with create schemas
from app.campaigns.schemas import CampaignFieldsBase, PaymentBlockFieldsBase
from app.deliverables.schemas import DeliverableFieldsBase

# =============================================================================
# EXTRACTION SCHEMAS - Used by AI agents, inherit from base + add metadata
# =============================================================================


class PaymentBlockExtractionSchema(PaymentBlockFieldsBase):
    """Schema for extracted payment block data.

    Inherits from PaymentBlockFieldsBase to stay in sync with payment block fields.
    """

    pass  # No additional fields needed for payment blocks


class DeliverableExtractionSchema(DeliverableFieldsBase):
    """Schema for extracted deliverable data.

    Inherits from DeliverableFieldsBase to stay in sync with deliverable fields.
    Adds extraction-specific metadata.
    """

    # Extraction metadata
    extraction_notes: str | None = None


class CampaignExtractionSchema(CampaignFieldsBase):
    """Schema for structured campaign data extracted by OpenAI agent.

    Inherits from CampaignFieldsBase to stay in sync with campaign fields.
    Adds extraction-specific metadata and nested extraction schemas.
    """

    # Nested extracted data
    payment_blocks: list[PaymentBlockExtractionSchema] = []
    deliverables: list[DeliverableExtractionSchema] = []

    # Extraction metadata
    confidence_score: float | None = None
    extraction_notes: str | None = None


class ExtractFromContractRequestSchema(BaseSchema):
    """Request schema for contract extraction endpoint."""

    document_id: str  # Sqid as string


class ExtractFromContractResponseSchema(BaseSchema):
    """Response schema for contract extraction endpoint."""

    data: CampaignExtractionSchema
    message: str = "Extraction completed successfully"
