from enum import StrEnum, auto


class CampaignStates(StrEnum):
    DRAFT = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class CampaignActions(StrEnum):
    """Campaign actions."""

    create = "campaign.create"
    delete = "campaign.delete"
    update = "campaign.update"
    add_deliverable = "campaign.add_deliverable"


class CompensationStructure(StrEnum):
    FLAT_FEE = auto()
    PER_DELIVERABLE = auto()
    PERFORMANCE_BASED = auto()


class CampaignGuestAccessLevel(StrEnum):
    """Access levels for campaign guests."""

    VIEWER = auto()  # Can view campaign data
    CONTRIBUTOR = auto()  # Can view and edit campaign data


class CounterpartyType(StrEnum):
    """Type of counterparty in a campaign deal."""

    AGENCY = auto()
    BRAND = auto()


class OwnershipMode(StrEnum):
    """Content ownership mode."""

    BRAND_OWNED = auto()
    CREATOR_OWNED = auto()
    SHARED = auto()
