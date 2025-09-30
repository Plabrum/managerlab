from enum import StrEnum, auto


class CampaignStates(StrEnum):
    DRAFT = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    CANCELLED = auto()
