from datetime import datetime
from typing import Any

from app.utils.sqids import Sqid
from app.base.schemas import BaseSchema
from app.deliverables.enums import SocialMediaPlatforms
from app.deliverables.models import Deliverable, DeliverableMedia
from app.media.schemas import MediaResponseSchema, media_to_response
from app.users.models import Roster
from app.actions.schemas import ActionDTO
from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry


# Response Schemas
class DeliverableMediaAssociationSchema(BaseSchema):
    """Association between deliverable and media with approval status."""

    approved_at: datetime | None
    is_featured: bool
    media: MediaResponseSchema
    created_at: datetime
    updated_at: datetime


class RosterInDeliverableSchema(BaseSchema):
    """Roster/talent as it appears in a deliverable."""

    id: Sqid
    name: str
    email: str | None
    instagram_handle: str | None
    facebook_handle: str | None
    tiktok_handle: str | None
    youtube_channel: str | None
    state: str


class DeliverableResponseSchema(BaseSchema):
    """Full deliverable response with nested relationships."""

    id: Sqid
    title: str
    content: str | None
    platforms: SocialMediaPlatforms
    posting_date: datetime
    notes: dict[str, Any]
    state: str
    campaign_id: int | None
    created_at: datetime
    updated_at: datetime

    # Nested relationships
    deliverable_media_associations: list[DeliverableMediaAssociationSchema]
    assigned_roster: RosterInDeliverableSchema | None

    # Actions
    actions: list[ActionDTO]


# Transformer functions
def deliverable_media_to_schema(
    dm: DeliverableMedia, s3_client
) -> DeliverableMediaAssociationSchema:
    """Transform DeliverableMedia association to schema.

    Args:
        dm: DeliverableMedia association instance
        s3_client: S3Client for generating presigned URLs
    """
    # Get media actions for nested media in deliverable context
    action_group = ActionRegistry().get_class(ActionGroupType.MediaActions)
    media_actions = action_group.get_available_actions(obj=dm.media)

    return DeliverableMediaAssociationSchema(
        approved_at=dm.approved_at,
        is_featured=dm.is_featured,
        media=media_to_response(dm.media, s3_client, media_actions),
        created_at=dm.created_at,
        updated_at=dm.updated_at,
    )


def roster_to_schema(roster: Roster) -> RosterInDeliverableSchema:
    """Transform Roster model to schema."""
    return RosterInDeliverableSchema(
        id=roster.id,  # Already a Sqid from the model
        name=roster.name,
        email=roster.email,
        instagram_handle=roster.instagram_handle,
        facebook_handle=roster.facebook_handle,
        tiktok_handle=roster.tiktok_handle,
        youtube_channel=roster.youtube_channel,
        state=roster.state,
    )


def deliverable_to_response(
    deliverable: Deliverable, s3_client
) -> DeliverableResponseSchema:
    """Transform Deliverable model to response schema.

    Args:
        deliverable: Deliverable model instance
        s3_client: S3Client for generating presigned URLs
    """
    # Compute available actions for this deliverable
    action_group = ActionRegistry().get_class(ActionGroupType.DeliverableActions)
    actions = action_group.get_available_actions(obj=deliverable)

    return DeliverableResponseSchema(
        id=deliverable.id,  # Already a Sqid from the model
        title=deliverable.title,
        content=deliverable.content,
        platforms=deliverable.platforms,
        posting_date=deliverable.posting_date,
        notes=deliverable.notes,
        state=deliverable.state,
        campaign_id=deliverable.campaign_id,
        created_at=deliverable.created_at,
        updated_at=deliverable.updated_at,
        deliverable_media_associations=[
            deliverable_media_to_schema(dm, s3_client)
            for dm in deliverable.deliverable_media_associations
        ],
        assigned_roster=(
            roster_to_schema(deliverable.assigned_roster)
            if deliverable.assigned_roster
            else None
        ),
        actions=actions,
    )


class DeliverableUpdateSchema(BaseSchema):
    """Schema for updating a Deliverable."""

    title: str | None = None
    content: str | None = None
    platforms: SocialMediaPlatforms | None = None
    posting_date: datetime | None = None
    notes: dict[str, Any] | None = None
    campaign_id: int | None = None


class DeliverableCreateSchema(BaseSchema):
    """Schema for creating a Deliverable."""

    title: str
    platforms: SocialMediaPlatforms
    posting_date: datetime
    content: str | None = None
    notes: dict[str, Any] | None = None
    campaign_id: int | None = None


class AddMediaToDeliverableSchema(BaseSchema):
    """Schema for adding media to a Deliverable."""

    media_ids: list[Sqid]


class RemoveMediaFromDeliverableSchema(BaseSchema):
    """Schema for removing media from a Deliverable."""

    media_ids: list[Sqid]
