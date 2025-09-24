"""Campaign object model."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.objects.models.base import BaseObject
from app.objects.enums import CampaignState

if TYPE_CHECKING:
    pass


class Campaign(BaseObject):
    """Campaign object model."""

    __tablename__ = "campaigns"

    # Campaign-specific fields
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Campaign details
    campaign_type: Mapped[str | None] = mapped_column(
        sa.String(100), nullable=True
    )  # email, social, ads, etc.
    platform: Mapped[str | None] = mapped_column(
        sa.String(100), nullable=True
    )  # facebook, instagram, google, etc.

    # Dates
    start_date: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    launch_date: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    # Budget and goals
    budget: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 2), nullable=True)
    spend: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(10, 2), nullable=True, default=0
    )
    target_impressions: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    target_clicks: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    target_conversions: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    # Performance metrics
    impressions: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, default=0
    )
    clicks: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, default=0)
    conversions: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, default=0
    )
    ctr: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(5, 4), nullable=True, default=0
    )  # Click-through rate
    cpc: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(10, 2), nullable=True, default=0
    )  # Cost per click

    # Targeting
    target_audience: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    demographics: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    interests: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    locations: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    # Creative assets
    creative_assets: Mapped[dict | None] = mapped_column(
        sa.JSON, nullable=True
    )  # URLs to images, videos, etc.
    ad_copy: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    call_to_action: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    # Relations
    brand_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    team_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    manager_user_id: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, index=True
    )

    # External platform data
    external_campaign_id: Mapped[str | None] = mapped_column(
        sa.String(255), nullable=True
    )
    platform_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    tags: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    def __init__(self, **kwargs):
        if "object_type" not in kwargs:
            kwargs["object_type"] = "campaign"
        if "state" not in kwargs:
            kwargs["state"] = CampaignState.DRAFT.value
        super().__init__(**kwargs)

    @property
    def budget_remaining(self) -> Decimal:
        """Calculate remaining budget."""
        if self.budget is None or self.spend is None:
            return Decimal(0)
        return self.budget - self.spend

    @property
    def conversion_rate(self) -> Decimal:
        """Calculate conversion rate."""
        if not self.clicks or not self.conversions:
            return Decimal(0)
        return Decimal(self.conversions) / Decimal(self.clicks)

    @property
    def is_active(self) -> bool:
        """Check if campaign is currently active."""
        return self.state == CampaignState.ACTIVE.value

    @property
    def is_completed(self) -> bool:
        """Check if campaign is completed."""
        if self.end_date:
            from datetime import date as date_module

            return date_module.today() > self.end_date
        return False
