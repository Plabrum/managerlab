from enum import StrEnum, auto


class PostStates(StrEnum):
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


class PostActions(StrEnum):
    """Actions for Post objects."""

    publish = "post.publish"
    delete = "post.delete"
    update = "post.update"


class TopLevelPostActions(StrEnum):
    """Top-level Post actions (no object context)."""

    create = "top_level_post.create"
