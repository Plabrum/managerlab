"""Team object model."""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.objects.models.base import BaseObject
from app.objects.enums import TeamStates

if TYPE_CHECKING:
    pass


class Team(BaseObject):
    """Team object model."""

    __tablename__ = "teams"
    _states_enum = TeamStates

    # Team-specific fields
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Team settings
    color: Mapped[str | None] = mapped_column(
        sa.String(7), nullable=True
    )  # Hex color code
    is_default: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    # Permissions and access
    permissions: Mapped[str | None] = mapped_column(
        sa.JSON, nullable=True
    )  # JSON object

    # Manager information
    manager_user_id: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, index=True
    )

    # Contact information
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    # Location
    location: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    timezone: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    def __init__(self, **kwargs):
        if "object_type" not in kwargs:
            kwargs["object_type"] = "team"
        if "state" not in kwargs:
            kwargs["state"] = TeamStates.ACTIVE
        super().__init__(**kwargs)
