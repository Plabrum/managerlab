"""Object state enums."""

from enum import Enum, auto


class InvoiceStates(str, Enum):
    DRAFT = auto()
    READY = auto()
    SENT = auto()
    PAID = auto()
    OVERDUE = auto()
    CANCELLED = auto()


class ContactStates(str, Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    ARCHIVED = auto()


class TeamStates(str, Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    ARCHIVED = auto()


class BrandStates(str, Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    ARCHIVED = auto()


class CampaignStates(str, Enum):
    DRAFT = auto()
    ACTIVE = auto()
    PAUSED = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class PostStates(str, Enum):
    DRAFT = auto()
    SCHEDULED = auto()
    PUBLISHED = auto()
    ARCHIVED = auto()


class MediaStates(str, Enum):
    UPLOADING = auto()
    PROCESSING = auto()
    READY = auto()
    ERROR = auto()
    ARCHIVED = auto()


class UserStates(str, Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    SUSPENDED = auto()
    ARCHIVED = auto()
