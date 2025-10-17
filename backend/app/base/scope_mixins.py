"""Scope mixins for multi-tenancy support.

These mixins provide team and campaign scoping for models.
Models inherit from these mixins to automatically get scope filtering.
"""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column


class TeamScopedMixin:
    """Mixin for models that are scoped to a team only.

    Examples: Brand, BrandContact, Campaign, Roster

    Team members can see all resources with their team_id.
    Campaign guests cannot access these resources.

    Uses RESTRICT on delete to prevent accidental data loss.
    Use soft delete (deleted_at) from BaseDBModel instead.
    """

    team_id: Mapped[int] = mapped_column(
        sa.ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )


class DualScopedMixin:
    """Mixin for models that are scoped to both team AND campaign.

    Examples: Post, Invoice, Media

    These models have both team_id and campaign_id:
    - Team members see all resources with their team_id (all campaigns)
    - Campaign guests see only resources with their specific campaign_id

    Note: team_id is denormalized from Campaign for efficient filtering.

    Uses RESTRICT on delete to prevent accidental data loss.
    Use soft delete (deleted_at) from BaseDBModel instead.
    """

    team_id: Mapped[int] = mapped_column(
        sa.ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    campaign_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("campaigns.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
