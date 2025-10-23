from __future__ import annotations

from typing import Any
import sqids as _sqids

__all__ = [
    "sqid_decode",
    "sqid_encode",
    "Sqid",
    "sqid_type_predicate",
    "sqid_enc_hook",
    "sqid_dec_hook",
]

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


class Sqid(int):
    """A distinct type for SQID values that behaves like int but triggers custom hooks.

    This allows msgspec to recognize it as a custom type and call our dec_hook.
    At runtime, it's a subclass of int, so it works seamlessly with database operations.
    """

    pass


# Type predicate for Litestar's type_decoders
def sqid_type_predicate(type_: type) -> bool:
    """Check if a type is Sqid."""
    return type_ is Sqid or (isinstance(type_, type) and issubclass(type_, Sqid))


# Encoder hook for Litestar's type_encoders (Sqid/int -> str)
def sqid_enc_hook(value: int) -> str:
    """Encode integer to SQID string for serialization."""
    return sqid_encode(value)


# Decoder hook for Litestar's type_decoders (str -> Sqid)
def sqid_dec_hook(type_: type, obj: Any) -> Sqid:
    """Decode SQID string to Sqid (int subclass) for deserialization."""
    if sqid_type_predicate(type_):
        if isinstance(obj, str):
            return Sqid(sqid_decode(obj))
        elif isinstance(obj, int):
            # Already an integer, wrap in Sqid
            return Sqid(obj)
        else:
            raise TypeError(
                f"Expected str or int for Sqid, got {type(obj).__name__}: {obj}"
            )
    raise NotImplementedError(f"Encountered unknown type: {type_}")
