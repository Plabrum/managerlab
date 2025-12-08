from enum import StrEnum, auto


class InvoiceStates(StrEnum):
    DRAFT = auto()
    POSTED = auto()


class InvoiceActions(StrEnum):
    """Invoice actions."""

    create = "invoice.create"
    delete = "invoice.delete"
    update = "invoice.update"
    update_state = "invoice.update_state"
