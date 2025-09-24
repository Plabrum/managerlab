"""Base object model for all objects in the platform."""

from typing import TYPE_CHECKING, Any, Dict

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
import sqids

from app.base.models import BaseDBModel

if TYPE_CHECKING:
    pass


# SQID encoder for external IDs
sqid_encoder = sqids.Sqids(min_length=8)


class BaseObject(BaseDBModel):
    """Base class for all objects in the platform."""

    __abstract__ = True

    # Object versioning for optimistic locking
    object_version: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, default=1, server_default=sa.text("1")
    )

    # Current state of the object
    state: Mapped[str] = mapped_column(sa.String(100), nullable=False, index=True)

    # Object type identifier (for polymorphic queries)
    object_type: Mapped[str] = mapped_column(sa.String(50), nullable=False, index=True)

    @property
    def sqid(self) -> str:
        """Generate SQID for external API usage."""
        return sqid_encoder.encode([self.id])

    @classmethod
    def decode_sqid(cls, sqid: str) -> int:
        """Decode SQID to internal ID."""
        decoded = sqid_encoder.decode(sqid)
        if not decoded:
            raise ValueError(f"Invalid SQID: {sqid}")
        return decoded[0]

    def increment_version(self) -> None:
        """Increment the object version for optimistic locking."""
        self.object_version += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including SQID."""
        result = super().to_dict()
        result["sqid"] = self.sqid
        return result
