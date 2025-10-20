"""Post object model."""

from datetime import datetime
from typing import Any, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableDict

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.posts.enums import CompensationStructure, PostStates, SocialMediaPlatforms
from app.state_machine.models import StateMachineMixin

if TYPE_CHECKING:
    from app.media.models import Media
    from app.campaigns.models import Campaign


class Post(
    RLSMixin(scope_with_campaign_id=True),
    StateMachineMixin(initial_state=PostStates.DRAFT, states=PostStates),
    BaseDBModel,
):
    """Post object model."""

    __tablename__ = "posts"

    # Post-specific fields
    title: Mapped[str] = mapped_column(sa.Text, nullable=False)
    content: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    platforms: Mapped[SocialMediaPlatforms] = mapped_column(
        sa.Enum(SocialMediaPlatforms), nullable=False
    )
    posting_date: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    notes: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )
    compensation_structure: Mapped[CompensationStructure] = mapped_column(
        sa.Enum(CompensationStructure),
        nullable=True,
    )

    # Relationships (campaign_id is from RLSMixin)
    campaign: Mapped["Campaign | None"] = relationship(
        "Campaign", back_populates="posts"
    )
    media: Mapped[list["Media"]] = relationship(
        "Media", secondary="post_media", back_populates="posts"
    )


# Association table for many-to-many relationship between posts and media
post_media = sa.Table(
    "post_media",
    BaseDBModel.metadata,
    sa.Column("post_id", sa.ForeignKey("posts.id"), primary_key=True),
    sa.Column("media_id", sa.ForeignKey("media.id"), primary_key=True),
)
