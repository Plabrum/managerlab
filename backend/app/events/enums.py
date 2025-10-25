from enum import StrEnum


class EventType(StrEnum):
    """Types of activity events that can be tracked."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STATE_CHANGED = "state_changed"
    CUSTOM = "custom"
