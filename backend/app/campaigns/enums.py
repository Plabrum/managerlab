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


class CompensationStructure(StrEnum):
    FLAT_FEE = auto()
    PER_DELIVERABLE = auto()
    PERFORMANCE_BASED = auto()


class CampaignGuestAccessLevel(StrEnum):
    """Access levels for campaign guests."""

    VIEWER = auto()  # Can view campaign data
    CONTRIBUTOR = auto()  # Can view and edit campaign data
