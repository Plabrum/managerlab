"""Email state enums."""

from enum import Enum


class EmailState(str, Enum):
    """Email message states."""

    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class InboundEmailState(str, Enum):
    """Inbound email processing states."""

    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
