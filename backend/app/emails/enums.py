"""Email state enums."""

from enum import Enum


class EmailState(str, Enum):
    """Email message states."""

    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
