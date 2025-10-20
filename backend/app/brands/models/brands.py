"""Brand object model."""

from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin

if TYPE_CHECKING:
    from app.campaigns.models import Campaign
    from app.brands.models.contacts import BrandContact


class Brand(RLSMixin(), BaseDBModel):
    """Brand object model."""

    __tablename__ = "brands"

    # Brand-specific fields
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Brand guidelines
    tone_of_voice: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    brand_values: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Contact information
    website: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    email: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Relationships
    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign", back_populates="brand"
    )
    contacts: Mapped[list["BrandContact"]] = relationship(
        "BrandContact", back_populates="brand"
    )
