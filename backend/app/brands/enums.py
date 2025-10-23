from enum import StrEnum, auto


class BrandStates(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()


class BrandActions(StrEnum):
    """Brand actions."""

    create = "brand.create"
    delete = "brand.delete"
    update = "brand.update"
