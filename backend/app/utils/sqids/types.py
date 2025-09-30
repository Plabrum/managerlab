from typing import Annotated, TypeAlias, Any
import sqids
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema

sqid_encoder = sqids.Sqids(alphabet="abcdefghijklmnopqrstuvwxyz", min_length=8)


def sqid_decode(value: str) -> int:
    """Decode SQID string to integer ID."""
    decoded = sqid_encoder.decode(value)
    if not decoded:
        raise ValueError(f"Invalid SQID: {value}")
    return decoded[0]


def sqid_encode(value: int) -> str:
    return sqid_encoder.encode([value])


def _to_int(v: Any) -> int:
    # Accept ints (already internal form) or sqid strings
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        return sqid_decode(v)
    raise TypeError("Sqid must be an int or sqid string")


# Sqid is an int at runtime, but:
# - INPUT: strings are decoded to int
# - OUTPUT (JSON): ints are encoded to sqid string
# - OPENAPI: documented as type: string
Sqid: TypeAlias = Annotated[
    int,
    BeforeValidator(_to_int),
    PlainSerializer(lambda v: sqid_encode(int(v)), when_used="json"),
    WithJsonSchema(
        {
            "type": "string",
            "title": "Sqid",
            "description": "SQIDs encoded as lowercase alphabet, min length 8",
            "pattern": "^[a-z]{8,}$",
        }
    ),
]
