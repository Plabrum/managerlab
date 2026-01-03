from datetime import date, datetime

from msgspec import UNSET, UnsetType

from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
from app.campaigns.enums import CompensationStructure, CounterpartyType, OwnershipMode
from app.deliverables.enums import SocialMediaPlatforms
from app.threads.schemas import ThreadUnreadInfo
from app.utils.sqids import Sqid

# =============================================================================
# BASE FIELD SCHEMAS - Shared between Create, Update, and Extraction schemas
# =============================================================================


class PaymentBlockFieldsBase(BaseSchema):
    """Base schema with core payment block fields.

    Inherited by:
    - PaymentBlockExtractionSchema (in agents/schemas.py)
    - Future: PaymentBlockCreateSchema if needed
    """

    label: str | None = None
    trigger: str | None = None
    amount_usd: float | None = None
    percent: float | None = None
    net_days: int | None = None


class CampaignFieldsBase(BaseSchema):
    """Base schema with core campaign fields.

    Inherited by:
    - CampaignCreateSchema (below)
    - CampaignExtractionSchema (in agents/schemas.py)

    Note: CampaignUpdateSchema intentionally duplicates these fields with UnsetType
    due to msgspec limitations. This is an acceptable trade-off for clarity.
    """

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


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class CampaignSchema(BaseSchema):
    """Manual schema for Campaign model."""

    id: Sqid
    name: str
    description: str | None
    compensation_structure: CompensationStructure | None
    assigned_roster_id: int | None
    brand_id: Sqid
    state: str
    created_at: datetime
    updated_at: datetime
    team_id: int | None
    actions: list[ActionDTO]
    thread: ThreadUnreadInfo | None = None

    # Counterparty
    counterparty_type: CounterpartyType | None = None
    counterparty_name: str | None = None
    counterparty_email: str | None = None

    # Compensation
    compensation_total_usd: float | None = None
    payment_terms_days: int | None = None

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


class CampaignUpdateSchema(BaseSchema):
    """Schema for updating a Campaign."""

    name: str | None | UnsetType = UNSET
    description: str | None | UnsetType = UNSET
    brand_id: int | None | UnsetType = UNSET
    compensation_structure: CompensationStructure | None | UnsetType = UNSET

    # Counterparty
    counterparty_type: CounterpartyType | None | UnsetType = UNSET
    counterparty_name: str | None | UnsetType = UNSET
    counterparty_email: str | None | UnsetType = UNSET

    # Compensation
    compensation_total_usd: float | None | UnsetType = UNSET
    payment_terms_days: int | None | UnsetType = UNSET

    # Flight dates
    flight_start_date: date | None | UnsetType = UNSET
    flight_end_date: date | None | UnsetType = UNSET

    # FTC & Usage
    ftc_string: str | None | UnsetType = UNSET
    usage_duration: str | None | UnsetType = UNSET
    usage_territory: str | None | UnsetType = UNSET
    usage_paid_media_option: bool | None | UnsetType = UNSET

    # Exclusivity
    exclusivity_category: str | None | UnsetType = UNSET
    exclusivity_days_before: int | None | UnsetType = UNSET
    exclusivity_days_after: int | None | UnsetType = UNSET

    # Ownership
    ownership_mode: OwnershipMode | None | UnsetType = UNSET

    # Approval
    approval_rounds: int | None | UnsetType = UNSET
    approval_sla_hours: int | None | UnsetType = UNSET


class CampaignCreateSchema(CampaignFieldsBase, kw_only=True):
    """Schema for creating a Campaign.

    Inherits from CampaignFieldsBase to stay in sync with campaign fields.
    Adds create-specific fields like brand_id and contract_document_id.

    Note: kw_only=True is required because we add required fields (brand_id)
    after inheriting from a base with optional fields.
    """

    # Create-specific fields
    brand_id: Sqid
    contract_document_id: Sqid | None = None


class AddDeliverableToCampaignSchema(BaseSchema):
    """Schema for adding a deliverable to a Campaign."""

    title: str
    platforms: SocialMediaPlatforms
    posting_date: datetime


class AddContractToCampaignSchema(BaseSchema):
    """Schema for adding initial contract to campaign."""

    document_id: Sqid


class ReplaceContractSchema(BaseSchema):
    """Schema for replacing existing contract with new version."""

    document_id: Sqid
