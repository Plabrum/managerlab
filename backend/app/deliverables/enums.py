from enum import StrEnum, auto


class DeliverableStates(StrEnum):
    DRAFT = auto()
    IN_REVIEW = auto()
    APPROVED = auto()
    POSTED = auto()


class SocialMediaPlatforms(StrEnum):
    INSTAGRAM = auto()
    FACEBOOK = auto()
    TIKTOK = auto()
    YOUTUBE = auto()


class CompensationStructure(StrEnum):
    FLAT_FEE = auto()
    PER_DELIVERABLE = auto()
    PERFORMANCE_BASED = auto()


class DeliverableActions(StrEnum):
    """Actions for Deliverable objects."""

    publish = "deliverable.publish"
    delete = "deliverable.delete"
    update = "deliverable.update"


class TopLevelDeliverableActions(StrEnum):
    """Top-level Deliverable actions (no object context)."""

    create = "top_level_deliverable.create"
