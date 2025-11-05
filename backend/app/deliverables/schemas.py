from datetime import date, datetime
from typing import Any

from msgspec import UNSET, UnsetType

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
from app.client.s3_client import S3Dep
from app.deliverables.enums import DeliverableType, SocialMediaPlatforms
from app.deliverables.models import Deliverable, DeliverableMedia
from app.media.schemas import MediaResponseSchema, media_to_response_schema
from app.roster.models import Roster
from app.threads.schemas import ThreadUnreadInfo
from app.utils.sqids import Sqid


# Response Schemas
class DeliverableMediaAssociationSchema(BaseSchema):
    """Association between deliverable and media with approval status."""

    id: Sqid
    approved_at: datetime | None
    is_featured: bool
    media: MediaResponseSchema
    created_at: datetime
    updated_at: datetime
    actions: list[ActionDTO]
    thread_id: Sqid | None


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
    deliverable_type: DeliverableType | None
    count: int
    posting_date: datetime
    posting_start_date: date | None
    posting_end_date: date | None

    # Caption requirements
    handles: list[str] | None
    hashtags: list[str] | None
    disclosures: list[str] | None

    # Approval
    approval_required: bool
    approval_rounds: int | None

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

    # Thread
    thread: ThreadUnreadInfo | None = None


# Transformer functions
def deliverable_media_to_schema(dm: DeliverableMedia, s3_client) -> DeliverableMediaAssociationSchema:
    """Transform DeliverableMedia association to schema.

    Args:
        dm: DeliverableMedia association instance
        s3_client: S3Client for generating presigned URLs
    """
    # Get media actions for nested media in deliverable context
    media_action_group = ActionRegistry().get_class(ActionGroupType.MediaActions)
    media_actions = media_action_group.get_available_actions(obj=dm.media)

    # Get deliverable media actions for the association
    deliverable_media_action_group = ActionRegistry().get_class(ActionGroupType.DeliverableMediaActions)
    deliverable_media_actions = deliverable_media_action_group.get_available_actions(obj=dm)

    return DeliverableMediaAssociationSchema(
        id=dm.id,
        approved_at=dm.approved_at,
        is_featured=dm.is_featured,
        media=media_to_response_schema(dm.media, s3_client, media_actions),
        created_at=dm.created_at,
        updated_at=dm.updated_at,
        actions=deliverable_media_actions,
        thread_id=dm.thread.id if dm.thread else None,
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
    deliverable: Deliverable,
    s3_client: S3Dep,
    actions: list[ActionDTO],
    thread_info: ThreadUnreadInfo | None,
) -> DeliverableResponseSchema:
    """Transform Deliverable model to response schema.

    Args:
        deliverable: Deliverable model instance
        s3_client: S3Client for generating presigned URLs
        user_id: User ID for calculating unread count
    """
    # Compute available actions for this deliverable

    return DeliverableResponseSchema(
        id=deliverable.id,  # Already a Sqid from the model
        title=deliverable.title,
        content=deliverable.content,
        platforms=deliverable.platforms,
        deliverable_type=deliverable.deliverable_type,
        count=deliverable.count,
        posting_date=deliverable.posting_date,
        posting_start_date=deliverable.posting_start_date,
        posting_end_date=deliverable.posting_end_date,
        handles=deliverable.handles,
        hashtags=deliverable.hashtags,
        disclosures=deliverable.disclosures,
        approval_required=deliverable.approval_required,
        approval_rounds=deliverable.approval_rounds,
        notes=deliverable.notes,
        state=deliverable.state,
        campaign_id=deliverable.campaign_id,
        created_at=deliverable.created_at,
        updated_at=deliverable.updated_at,
        deliverable_media_associations=[
            deliverable_media_to_schema(dm, s3_client) for dm in deliverable.deliverable_media_associations
        ],
        assigned_roster=(roster_to_schema(deliverable.assigned_roster) if deliverable.assigned_roster else None),
        actions=actions,
        thread=thread_info,
    )


class DeliverableUpdateSchema(BaseSchema):
    """Schema for updating a Deliverable."""

    title: str | None | UnsetType = UNSET
    content: str | None | UnsetType = UNSET
    platforms: SocialMediaPlatforms | None | UnsetType = UNSET
    deliverable_type: DeliverableType | None | UnsetType = UNSET
    count: int | None | UnsetType = UNSET
    posting_date: datetime | None | UnsetType = UNSET
    posting_start_date: date | None | UnsetType = UNSET
    posting_end_date: date | None | UnsetType = UNSET

    # Caption requirements
    handles: list[str] | None | UnsetType = UNSET
    hashtags: list[str] | None | UnsetType = UNSET
    disclosures: list[str] | None | UnsetType = UNSET

    # Approval
    approval_required: bool | None | UnsetType = UNSET
    approval_rounds: int | None | UnsetType = UNSET

    notes: dict[str, Any] | None | UnsetType = UNSET
    campaign_id: int | None | UnsetType = UNSET


class DeliverableCreateSchema(BaseSchema):
    """Schema for creating a Deliverable."""

    title: str
    platforms: SocialMediaPlatforms
    posting_date: datetime
    deliverable_type: DeliverableType | None = None
    count: int = 1
    posting_start_date: date | None = None
    posting_end_date: date | None = None

    # Caption requirements
    handles: list[str] | None = None
    hashtags: list[str] | None = None
    disclosures: list[str] | None = None

    # Approval
    approval_required: bool = True
    approval_rounds: int | None = None

    content: str | None = None
    notes: dict[str, Any] | None = None
    campaign_id: int | None = None


class AddMediaToDeliverableSchema(BaseSchema):
    """Schema for adding media to a Deliverable."""

    media_ids: list[Sqid]
