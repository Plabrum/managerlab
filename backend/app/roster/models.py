from datetime import date
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.base.threadable_mixin import ThreadableMixin
from app.roster.enums import RosterStates
from app.state_machine.models import StateMachineMixin

if TYPE_CHECKING:
    from app.addresses.models import Address
    from app.campaigns.models import Campaign
    from app.media.models import Media
    from app.users.models import User


class Roster(
    ThreadableMixin,
    RLSMixin(),
    StateMachineMixin(
        state_enum=RosterStates,
        initial_state=RosterStates.PROSPECT,
    ),
    BaseDBModel,
):
    """Talent/influencer with their own login - part of the object platform."""

    __tablename__ = "roster"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic fields
    name: Mapped[str] = mapped_column(sa.Text, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(sa.Text, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    birthdate: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    @property
    def age(self) -> int | None:
        if self.birthdate:
            today = date.today()
            return (today.year - self.birthdate.year) - (
                (today.month, today.day) < (self.birthdate.month, self.birthdate.day)
            )

    instagram_handle: Mapped[str | None] = mapped_column(sa.Text, nullable=True, index=True)
    facebook_handle: Mapped[str | None] = mapped_column(sa.Text, nullable=True, index=True)
    tiktok_handle: Mapped[str | None] = mapped_column(sa.Text, nullable=True, index=True)
    youtube_channel: Mapped[str | None] = mapped_column(sa.Text, nullable=True, index=True)

    # Profile photo
    profile_photo_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("media.id", ondelete="SET NULL", use_alter=True, name="fk_roster_profile_photo"),
        nullable=True,
        index=True,
    )

    # Address relationship
    address_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("addresses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationship to user (who owns/manages this roster member)
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    # Relationship to address
    address: Mapped["Address | None"] = relationship(
        "Address",
        foreign_keys=[address_id],
        lazy="joined",
    )

    # Relationship to profile photo
    profile_photo: Mapped["Media | None"] = relationship(
        "Media",
        foreign_keys=[profile_photo_id],
    )

    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign",
        back_populates="assigned_roster",
        primaryjoin="Roster.id == Campaign.assigned_roster_id",
        foreign_keys="Campaign.assigned_roster_id",
    )
