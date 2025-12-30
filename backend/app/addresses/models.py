"""Address models."""

import sqlalchemy as sa
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin


class Address(RLSMixin(), BaseDBModel):
    """Address model that can be referenced by multiple entities (roster, brands, campaigns, etc.)."""

    __tablename__ = "addresses"

    # Address fields
    address1: Mapped[str] = mapped_column(Text, nullable=False)
    address2: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zip: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(
        String(2), nullable=False, default="US"
    )  # ISO country code

    # Optional metadata
    address_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # "home", "work", "billing", etc.

    def __repr__(self) -> str:
        """String representation of address."""
        return f"<Address {self.address1}, {self.city}, {self.state} {self.zip}>"
