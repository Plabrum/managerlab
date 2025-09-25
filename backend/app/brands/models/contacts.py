"""Contact object model."""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import BaseDBModel


if TYPE_CHECKING:
    pass


class BrandContact(BaseDBModel):
    """Contact object model."""

    __tablename__ = "brand_contacts"

    # Contact-specific fields
    first_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    last_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    email: Mapped[str | None] = mapped_column(sa.Text, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
