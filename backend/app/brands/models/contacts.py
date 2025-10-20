"""Contact object model."""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin


if TYPE_CHECKING:
    from app.brands.models.brands import Brand
    from app.campaigns.models import Campaign


class BrandContact(RLSMixin(), BaseDBModel):
    """Contact object model."""

    __tablename__ = "brand_contacts"

    # Contact-specific fields
    first_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    last_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    email: Mapped[str | None] = mapped_column(sa.Text, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Foreign keys
    brand_id: Mapped[int] = mapped_column(sa.ForeignKey("brands.id"), nullable=False)

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="contacts")
    campaigns_as_lead: Mapped[list["Campaign"]] = relationship(
        "Campaign", secondary="campaign_lead_contacts", back_populates="lead_contacts"
    )
