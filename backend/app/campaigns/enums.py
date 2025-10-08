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
