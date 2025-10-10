from app.base.schemas import (
    CreateSQLAlchemyDTO,
    SanitizedSQLAlchemyDTO,
    UpdateSQLAlchemyDTO,
)
from app.payments.models import Invoice


class InvoiceDTO(SanitizedSQLAlchemyDTO[Invoice]):
    """Data transfer object for Invoice model."""

    pass


class InvoiceUpdateDTO(UpdateSQLAlchemyDTO[Invoice]):
    """DTO for partial Invoice updates."""

    pass


class InvoiceCreateDTO(CreateSQLAlchemyDTO[Invoice]):
    """DTO for partial Invoice updates."""

    pass
