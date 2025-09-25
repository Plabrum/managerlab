"""Brand object model."""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.objects.models.base import BaseObject


class Brand(BaseObject):
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
