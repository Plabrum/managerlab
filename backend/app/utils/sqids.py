from typing import Annotated
import sqids

sqid_encoder = sqids.Sqids(alphabet="abcdefghijklmnopqrstuvwxyz", min_length=8)


def sqid_decode(value: str) -> int:
    """Decode SQID string to integer ID."""
    decoded = sqid_encoder.decode(value)
    if not decoded:
        raise ValueError(f"Invalid SQID: {value}")
    return decoded[0]


def sqid_encode(value: int) -> str:
    return sqid_encoder.encode([value])


Sqid = Annotated[str, sqid_decode]
