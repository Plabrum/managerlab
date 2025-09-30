"""Media object model."""

from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel

if TYPE_CHECKING:
    from app.posts.models import Post


class Media(BaseDBModel):
    """Media object model."""

    __tablename__ = "media"

    # Media-specific fields
    filename: Mapped[str] = mapped_column(sa.Text, nullable=False)
    image_link: Mapped[str] = mapped_column(sa.Text, nullable=False)
    thumnbnail_link: Mapped[str] = mapped_column(sa.Text, nullable=True)

    # Relationships
    posts: Mapped[list["Post"]] = relationship(
        "Post", secondary="post_media", back_populates="media"
    )
