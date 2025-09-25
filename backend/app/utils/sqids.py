from typing import Annotated
import sqids

from app.base.schemas import BaseSchema

sqid_encoder = sqids.Sqids(min_length=8)


def sqid_decode(value: str) -> int:
    """Decode SQID string to integer ID."""
    decoded = sqid_encoder.decode(value)
    if not decoded:
        raise ValueError(f"Invalid SQID: {value}")
    return decoded[0]


# Route parameter type: SQID string → int
Sqid = Annotated[int, sqid_decode]


# Response DTO type: int → SQID string in JSON
class SqidDTO(BaseSchema):
    value: int

    class Config:
        json_encoders = {int: lambda value: sqid_encoder.encode([value])}
