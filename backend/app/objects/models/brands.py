"""Brand object model."""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.objects.models.base import BaseObject
from app.objects.enums import BrandState

if TYPE_CHECKING:
    pass


class Brand(BaseObject):
    """Brand object model."""

    __tablename__ = "brands"

    # Brand-specific fields
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Brand identity
    logo_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    primary_color: Mapped[str | None] = mapped_column(
        sa.String(7), nullable=True
    )  # Hex color
    secondary_color: Mapped[str | None] = mapped_column(
        sa.String(7), nullable=True
    )  # Hex color
    font_family: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    # Brand assets
    brand_assets: Mapped[dict | None] = mapped_column(
        sa.JSON, nullable=True
    )  # URLs to assets

    # Brand guidelines
    tone_of_voice: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    brand_values: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Contact information
    website: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    # Social media
    social_handles: Mapped[dict | None] = mapped_column(
        sa.JSON, nullable=True
    )  # Platform -> handle mapping

    # Business information
    industry: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    company_size: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    def __init__(self, **kwargs):
        if "object_type" not in kwargs:
            kwargs["object_type"] = "brand"
        if "state" not in kwargs:
            kwargs["state"] = BrandState.ACTIVE.value
        super().__init__(**kwargs)
