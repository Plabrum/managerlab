import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import BaseDBModel
from app.campaigns.enums import CampaignPlatforms


class Campaign(BaseDBModel):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    platform: Mapped[CampaignPlatforms] = mapped_column(sa.Text, nullable=True)
