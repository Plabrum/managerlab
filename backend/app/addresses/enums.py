"""Address-related enumerations."""

from enum import StrEnum


class AddressType(StrEnum):
    """Types of addresses."""

    HOME = "home"
    WORK = "work"
    OTHER = "other"
