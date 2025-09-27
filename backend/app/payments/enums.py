from enum import StrEnum, auto


class InvoiceStates(StrEnum):
    DRAFT = auto()
    POSTED = auto()
