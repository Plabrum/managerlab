"""Brand object model."""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.base.threadable_mixin import ThreadableMixin

if TYPE_CHECKING:
    from app.brands.models.contacts import BrandContact
    from app.campaigns.models import Campaign


class Brand(ThreadableMixin, RLSMixin(), BaseDBModel):
    """Brand object model."""

    __tablename__ = "brands"
    __table_args__ = (Index("ix_brands_team_id_name_lower", "team_id", "name", unique=True),)

    # Brand-specific fields
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Contact information
    website: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    email: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Relationships
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="brand")
    contacts: Mapped[list["BrandContact"]] = relationship("BrandContact", back_populates="brand")
