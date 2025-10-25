from __future__ import annotations

from typing import Any
import sqids as _sqids
from sqlalchemy import TypeDecorator, Integer

__all__ = [
    "sqid_decode",
    "sqid_encode",
    "Sqid",
    "SqidType",
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
    def __int__(self) -> int:
        return int.__new__(int, super().__int__())

    def __str__(self) -> str:
        return sqid_encode(int(self))


class SqidType(TypeDecorator):
    """SQLAlchemy type that stores int in DB but returns Sqid instances in Python.

    This ensures that when SQLAlchemy loads rows from the database, the id field
    is automatically wrapped as a Sqid instance, which triggers proper encoding
    when serialized by Litestar.
    """

    impl = Integer
    cache_ok = True

    def process_result_value(self, value: int | None, dialect) -> Sqid | None:
        """Convert int from DB to Sqid instance."""
        if value is not None:
            return Sqid(value)
        return value

    def process_bind_param(self, value: Any, dialect) -> int | None:
        """Convert Sqid to int for DB storage."""
        if value is not None:
            return int(value)
        return value


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
