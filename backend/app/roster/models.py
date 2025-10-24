from datetime import date
from sqlalchemy.orm import mapped_column, relationship, Mapped
import sqlalchemy as sa
from typing import TYPE_CHECKING
from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.state_machine.models import StateMachineMixin
from app.roster.enums import RosterStates


if TYPE_CHECKING:
    from app.users.models import User
    from app.campaigns.models import Campaign
    from app.media.models import Media


class Roster(
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

    @property
    def age(self) -> int | None:
        if self.birthdate:
            today = date.today()
            return (today.year - self.birthdate.year) - (
                (today.month, today.day) < (self.birthdate.month, self.birthdate.day)
            )

    instagram_handle: Mapped[str | None] = mapped_column(
        sa.Text, nullable=True, index=True
    )
    facebook_handle: Mapped[str | None] = mapped_column(
        sa.Text, nullable=True, index=True
    )
    tiktok_handle: Mapped[str | None] = mapped_column(
        sa.Text, nullable=True, index=True
    )
    youtube_channel: Mapped[str | None] = mapped_column(
        sa.Text, nullable=True, index=True
    )

    # Profile photo
    profile_photo_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("media.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationship to user (who owns/manages this roster member)
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

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
