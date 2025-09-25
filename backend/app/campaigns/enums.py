from enum import StrEnum, auto


class CampaignPlatforms(StrEnum):
    Instagram = auto()
    Facebook = auto()
    Tiktok = auto()
    Youtube = auto()


class CampaignStates(StrEnum):
    DRAFT = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    CANCELLED = auto()
