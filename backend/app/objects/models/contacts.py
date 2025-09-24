"""Contact object model."""

from datetime import date
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.objects.models.base import BaseObject
from app.objects.enums import ContactState

if TYPE_CHECKING:
    pass


class Contact(BaseObject):
    """Contact object model."""

    __tablename__ = "contacts"

    # Contact-specific fields
    first_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    # Company information
    company: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    job_title: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    # Address fields
    address_line1: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    state_province: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    country: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    # Social/Web
    website: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)

    # Dates
    date_of_birth: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    last_contact_date: Mapped[date | None] = mapped_column(sa.Date, nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(
        sa.Text, nullable=True
    )  # JSON array as string

    def __init__(self, **kwargs):
        if "object_type" not in kwargs:
            kwargs["object_type"] = "contact"
        if "state" not in kwargs:
            kwargs["state"] = ContactState.ACTIVE.value
        super().__init__(**kwargs)

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self) -> str:
        """Get display name with company if available."""
        name = self.full_name
        if self.company:
            name += f" ({self.company})"
        return name
