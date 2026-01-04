"""Deliverable object model."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.base.threadable_mixin import ThreadableMixin
from app.deliverables.enums import (
    DeliverableStates,
    DeliverableType,
    SocialMediaPlatforms,
)
from app.state_machine.models import StateMachineMixin
from app.utils.sqids import Sqid

if TYPE_CHECKING:
    from app.campaigns.models import Campaign
    from app.media.models import Media
    from app.roster.models import Roster


class Deliverable(
    ThreadableMixin,
    RLSMixin(scope_with_campaign_id=True),
    StateMachineMixin(initial_state=DeliverableStates.DRAFT, state_enum=DeliverableStates),
    BaseDBModel,
):
    """Deliverable object model."""

    __tablename__ = "deliverables"

    # Deliverable-specific fields
    title: Mapped[str] = mapped_column(sa.Text, nullable=False)
    content: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Platform and type
    platforms: Mapped[SocialMediaPlatforms] = mapped_column(sa.Enum(SocialMediaPlatforms), nullable=False)
    deliverable_type: Mapped[DeliverableType | None] = mapped_column(sa.Enum(DeliverableType), nullable=True)
    count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)

    # Posting dates - keep datetime for backward compatibility, add date range
    posting_date: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    posting_start_date: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    posting_end_date: Mapped[date | None] = mapped_column(sa.Date, nullable=True)

    # Caption requirements (stored as JSON arrays)
    handles: Mapped[list[str] | None] = mapped_column(ARRAY(sa.String), nullable=True, default=[])
    hashtags: Mapped[list[str] | None] = mapped_column(ARRAY(sa.String), nullable=True, default=[])
    disclosures: Mapped[list[str] | None] = mapped_column(ARRAY(sa.String), nullable=True, default=[])

    # Approval settings
    approval_required: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)
    approval_rounds: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, default=1)

    # General notes (JSONB for flexibility)
    notes: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    # Relationships (campaign_id is from RLSMixin)
    campaign: Mapped["Campaign | None"] = relationship("Campaign", back_populates="deliverables")
    assigned_roster: Mapped["Roster | None"] = relationship(
        "Roster",
        secondary="campaigns",
        primaryjoin="Deliverable.campaign_id == Campaign.id",
        secondaryjoin="Campaign.assigned_roster_id == Roster.id",
        viewonly=True,
        uselist=False,
    )
    media: Mapped[list["Media"]] = relationship(
        "Media",
        secondary="deliverable_media",
        back_populates="deliverables",
        viewonly=True,
    )
    deliverable_media_associations: Mapped[list["DeliverableMedia"]] = relationship(
        "DeliverableMedia",
        back_populates="deliverable",
        cascade="all, delete-orphan",
        overlaps="media,deliverables",
    )


class DeliverableMedia(ThreadableMixin, RLSMixin(scope_with_campaign_id=True), BaseDBModel):
    """Association model for deliverable-media relationship with approval status."""

    __tablename__ = "deliverable_media"

    deliverable_id: Mapped[Sqid] = mapped_column(
        sa.ForeignKey("deliverables.id", ondelete="CASCADE"),
        nullable=False,
    )
    media_id: Mapped[Sqid] = mapped_column(
        sa.ForeignKey("media.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Approval status for this media in this deliverable
    # If approved_at is not null, the media is approved
    approved_at: Mapped[datetime | None] = mapped_column(sa.DateTime, nullable=True)

    # Which media should be featured in the preview (only one per deliverable)
    is_featured: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False, server_default=sa.false())

    # Relationships
    deliverable: Mapped["Deliverable"] = relationship(
        "Deliverable",
        back_populates="deliverable_media_associations",
        overlaps="media,deliverables",
    )
    media: Mapped["Media"] = relationship(
        "Media",
        back_populates="deliverable_media_associations",
        overlaps="media,deliverables",
    )
