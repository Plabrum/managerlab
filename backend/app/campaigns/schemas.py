from datetime import datetime, date
from app.base.schemas import BaseSchema
from app.campaigns.enums import CompensationStructure, CounterpartyType, OwnershipMode
from app.utils.sqids import Sqid
from app.actions.schemas import ActionDTO


class CampaignSchema(BaseSchema):
    """Manual schema for Campaign model."""

    id: Sqid
    name: str
    description: str | None
    compensation_structure: CompensationStructure | None
    assigned_roster_id: int | None
    brand_id: int
    state: str
    created_at: datetime
    updated_at: datetime
    team_id: int | None
    actions: list[ActionDTO]

    # Counterparty
    counterparty_type: CounterpartyType | None
    counterparty_name: str | None
    counterparty_email: str | None

    # Compensation
    compensation_total_usd: float | None
    payment_terms_days: int | None

    # Flight dates
    flight_start_date: date | None
    flight_end_date: date | None

    # FTC & Usage
    ftc_string: str | None
    usage_duration: str | None
    usage_territory: str | None
    usage_paid_media_option: bool | None

    # Exclusivity
    exclusivity_category: str | None
    exclusivity_days_before: int | None
    exclusivity_days_after: int | None

    # Ownership
    ownership_mode: OwnershipMode | None

    # Approval
    approval_rounds: int | None
    approval_sla_hours: int | None


class CampaignUpdateSchema(BaseSchema):
    """Schema for updating a Campaign."""

    name: str | None = None
    description: str | None = None
    brand_id: int | None = None
    compensation_structure: CompensationStructure | None = None

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


class CampaignCreateSchema(BaseSchema):
    """Schema for creating a Campaign."""

    name: str
    brand_id: Sqid
    description: str | None = None
    compensation_structure: CompensationStructure | None = None

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
