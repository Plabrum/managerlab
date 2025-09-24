"""Post object model."""

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.objects.models.base import BaseObject
from app.objects.enums import PostState

if TYPE_CHECKING:
    pass


class Post(BaseObject):
    """Post object model."""

    __tablename__ = "posts"

    # Post-specific fields
    title: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    content: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    excerpt: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)

    # Post type and platform
    post_type: Mapped[str | None] = mapped_column(
        sa.String(100), nullable=True
    )  # article, social, video, etc.
    platform: Mapped[str | None] = mapped_column(
        sa.String(100), nullable=True
    )  # instagram, facebook, linkedin, etc.

    # Scheduling
    scheduled_date: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    published_date: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    # SEO and metadata
    slug: Mapped[str | None] = mapped_column(sa.String(500), nullable=True, index=True)
    meta_title: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    keywords: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Media
    featured_image_url: Mapped[str | None] = mapped_column(
        sa.String(500), nullable=True
    )
    media_urls: Mapped[dict | None] = mapped_column(
        sa.JSON, nullable=True
    )  # Array of media URLs
    alt_text: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    # Social media specific
    hashtags: Mapped[dict | None] = mapped_column(
        sa.JSON, nullable=True
    )  # Array of hashtags
    mentions: Mapped[dict | None] = mapped_column(
        sa.JSON, nullable=True
    )  # Array of mentions
    location_tag: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    # Performance metrics
    views: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, default=0)
    likes: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, default=0)
    shares: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, default=0)
    comments: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, default=0)
    engagement_rate: Mapped[float | None] = mapped_column(
        sa.Float, nullable=True, default=0.0
    )

    # Relations
    campaign_id: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, index=True
    )
    brand_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    author_user_id: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, index=True
    )

    # External platform data
    external_post_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    external_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    platform_data: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    # Content settings
    is_featured: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    allow_comments: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, nullable=False
    )
    content_warning: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    # Categories and tags
    categories: Mapped[dict | None] = mapped_column(
        sa.JSON, nullable=True
    )  # Array of categories
    tags: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)  # Array of tags

    # Notes
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    def __init__(self, **kwargs):
        if "object_type" not in kwargs:
            kwargs["object_type"] = "post"
        if "state" not in kwargs:
            kwargs["state"] = PostState.DRAFT.value
        super().__init__(**kwargs)

    @property
    def is_published(self) -> bool:
        """Check if post is published."""
        return self.state == PostState.PUBLISHED.value

    @property
    def is_scheduled(self) -> bool:
        """Check if post is scheduled."""
        return (
            self.state == PostState.SCHEDULED.value and self.scheduled_date is not None
        )

    @property
    def total_engagement(self) -> int:
        """Calculate total engagement."""
        return (self.likes or 0) + (self.shares or 0) + (self.comments or 0)

    @property
    def word_count(self) -> int:
        """Count words in content."""
        if not self.content:
            return 0
        return len(self.content.split())
