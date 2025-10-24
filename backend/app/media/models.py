"""Media object model."""

from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.base.threadable_mixin import ThreadableMixin
from app.media.enums import MediaStates
from app.state_machine.models import StateMachineMixin

if TYPE_CHECKING:
    from app.deliverables.models import Deliverable, DeliverableMedia


class Media(
    ThreadableMixin,
    RLSMixin(scope_with_campaign_id=True),
    StateMachineMixin(state_enum=MediaStates, initial_state=MediaStates.PENDING),
    BaseDBModel,
):
    """Media object model for photos and videos."""

    __tablename__ = "media"

    # File metadata
    file_key: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    file_type: Mapped[str] = mapped_column(
        sa.Text, nullable=False
    )  # 'image' or 'video'
    file_size: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # Thumbnail
    thumbnail_key: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Relationships
    # The deliverable_media association table is defined in app.deliverables.models
    deliverables: Mapped[list["Deliverable"]] = relationship(
        "Deliverable",
        secondary="deliverable_media",
        back_populates="media",
        viewonly=True,
    )
    deliverable_media_associations: Mapped[list["DeliverableMedia"]] = relationship(
        "DeliverableMedia",
        back_populates="media",
        cascade="all, delete-orphan",
        overlaps="media,deliverables",
    )
