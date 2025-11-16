"""Schemas for AI agent extraction outputs."""

from datetime import date

from app.base.schemas import BaseSchema
from app.campaigns.enums import CompensationStructure, CounterpartyType, OwnershipMode


class PaymentBlockExtractionSchema(BaseSchema):
    """Schema for extracted payment block data."""

    label: str | None = None
    trigger: str | None = None
    amount_usd: float | None = None
    percent: float | None = None
    net_days: int | None = None


class CampaignExtractionSchema(BaseSchema):
    """Schema for structured campaign data extracted by OpenAI agent.

    This schema matches CampaignCreateSchema but includes additional metadata
    from the extraction process (confidence score, notes).
    """

    # Required fields
    name: str
    description: str | None = None

    # Counterparty
    counterparty_type: CounterpartyType | None = None
    counterparty_name: str | None = None
    counterparty_email: str | None = None

    # Compensation
    compensation_structure: CompensationStructure | None = None
    compensation_total_usd: float | None = None
    payment_terms_days: int | None = None

    # Payment schedule
    payment_blocks: list[PaymentBlockExtractionSchema] = []

    # Flight dates
    flight_start_date: date | None = None
    flight_end_date: date | None = None

    # FTC & Usage
    ftc_string: str | None = None
    usage_duration: str | None = None
    usage_territory: str | None = None
    usage_paid_media_option: bool | None = None

    # Exclusivity
    exclusivity_category: str | None = None
    exclusivity_days_before: int | None = None
    exclusivity_days_after: int | None = None

    # Ownership
    ownership_mode: OwnershipMode | None = None

    # Approval
    approval_rounds: int | None = None
    approval_sla_hours: int | None = None

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
