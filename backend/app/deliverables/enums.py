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

    create = "deliverable.create"
    publish = "deliverable.publish"
    delete = "deliverable.delete"
    update = "deliverable.update"
    add_media = "deliverable.add_media"
    update_state = "deliverable.update_state"


class DeliverableMediaActions(StrEnum):
    """Actions for DeliverableMedia association objects."""

    remove_media = "deliverable_media.remove_media"
    accept = "deliverable_media.accept"
    reject = "deliverable_media.reject"


class DeliverableType(StrEnum):
    """Types of deliverables for various platforms."""

    # Instagram
    INSTAGRAM_FEED_POST = auto()
    INSTAGRAM_STORY_FRAME = auto()
    INSTAGRAM_REEL = auto()
    INSTAGRAM_CAROUSEL = auto()

    # TikTok
    TIKTOK_VIDEO = auto()
    TIKTOK_PHOTO_POST = auto()

    # YouTube
    YOUTUBE_VIDEO = auto()
    YOUTUBE_SHORT = auto()
    YOUTUBE_COMMUNITY_POST = auto()

    # Facebook
    FACEBOOK_POST = auto()
    FACEBOOK_STORY = auto()
    FACEBOOK_REEL = auto()

    # Other
    BLOG_POST = auto()
    PODCAST_EPISODE = auto()
    EMAIL_NEWSLETTER = auto()
