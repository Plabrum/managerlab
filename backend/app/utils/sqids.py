from __future__ import annotations

from typing import Annotated, TypeAlias
import sqids as _sqids

__all__ = ["sqid_decode", "sqid_encode", "Sqid"]

sqid_encoder: _sqids.Sqids = _sqids.Sqids(
    alphabet="abcdefghijklmnopqrstuvwxyz", min_length=8
)


def sqid_decode(value: str) -> int:
    """Decode SQID string to integer ID."""
    decoded = sqid_encoder.decode(value)
    if not decoded:
        raise ValueError(f"Invalid SQID: {value}")
    return decoded[0]


def sqid_encode(value: int) -> str:
    """Encode integer ID to SQID string."""
    return sqid_encoder.encode([value])


Sqid: TypeAlias = Annotated[str, sqid_decode]
