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


class DeliverableActions(StrEnum):
    """Actions for Deliverable objects."""

    publish = "deliverable.publish"
    delete = "deliverable.delete"
    update = "deliverable.update"
    add_media = "deliverable.add_media"
    remove_media = "deliverable.remove_media"


class TopLevelDeliverableActions(StrEnum):
    """Top-level Deliverable actions (no object context)."""

    create = "top_level_deliverable.create"
