"""Media object model."""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import BaseDBModel


class Media(BaseDBModel):
    """Media object model."""

    __tablename__ = "media"

    # Media-specific fields
    filename: Mapped[str] = mapped_column(sa.Text, nullable=False)
