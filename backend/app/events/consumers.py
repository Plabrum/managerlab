import logging
from typing import Any

from litestar.channels import ChannelsPlugin
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.models import BaseDBModel
from app.brands.models.brands import Brand
from app.campaigns.models import Campaign
from app.deliverables.models import DeliverableMedia
from app.events.enums import EventType
from app.events.models import Event
from app.events.registry import event_consumer
from app.events.schemas import FieldChange, UpdatedEventData
from app.roster.models import Roster
from app.threads.enums import ThreadSocketMessageType
from app.threads.models import Message
from app.threads.schemas import ServerMessage
from app.threads.services import (
    get_or_create_thread,
    notify_thread,
)
from app.utils.sqids import sqid_encode
from app.utils.tiptap import bold, doc, paragraph, text

logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions
# ============================================================================


async def _post_to_thread(
    session: AsyncSession,
    event: Event,
    content: dict,
    user_id: int | None,
    channels: ChannelsPlugin,
    campaign_id: int | None = None,
) -> None:
    """
    Helper to post a message to an object's thread.

    Args:
        session: Database session
        event: The event that triggered this
        content: TipTap content to post
        user_id: User ID for the message (None for system messages)
        channels: ChannelsPlugin instance from DI
        campaign_id: Optional campaign_id for dual-scoped messages
    """
    # Get or create thread for this object
    thread = await get_or_create_thread(
        transaction=session,
        threadable_type=event.object_type,
        threadable_id=event.object_id,
        team_id=event.team_id,
    )

    # Create thread message
    thread_message = Message(
        thread_id=thread.id,
        user_id=user_id,
        content=content,
        team_id=event.team_id,
        campaign_id=campaign_id,
    )
    session.add(thread_message)
    await session.flush()

    # Notify WebSocket subscribers
    # Event messages are system-created messages
    await notify_thread(
        channels,
        thread.id,
        ServerMessage(
            message_type=ThreadSocketMessageType.MESSAGE_CREATED,
            message_id=sqid_encode(thread_message.id),
            thread_id=sqid_encode(thread.id),
            user_id=sqid_encode(0),  # System user (events have no user_id)
            viewers=[],  # Empty - event consumers don't have viewer_store access
        ),
    )

    logger.info(f"Posted event {event.id} to thread {thread.id} as message {thread_message.id}")


def _format_object_ref(event: Event, obj: Any) -> str:
    """
    Format object reference for display using object name/title.

    Falls back to ID if no name attribute is found.
    """
    object_type_display = event.object_type.replace("_", " ").title()

    # Try common name attributes
    for attr in ["name", "title", "display_name"]:
        if hasattr(obj, attr):
            value = getattr(obj, attr)
            if value:
                return f"{object_type_display}: {value}"

    # Fallback to ID if no name found
    return f"{object_type_display} {sqid_encode(event.object_id)}"


def _parse_event_data_to_updated(
    event_data: dict[str, Any] | None,
) -> UpdatedEventData | None:
    if not event_data:
        return None

    # Check if this is already structured with "changes" wrapper
    if "changes" in event_data and isinstance(event_data["changes"], dict):
        # Already in UpdatedEventData format from database
        changes_dict = event_data["changes"]
    else:
        # Raw format - use directly
        changes_dict = event_data

    changes: dict[str, FieldChange] = {}
    for field_name, change_data in changes_dict.items():
        if isinstance(change_data, dict) and "old" in change_data and "new" in change_data:
            changes[field_name] = FieldChange(old=change_data["old"], new=change_data["new"])

    return UpdatedEventData(changes=changes) if changes else None


def build_update_message_content(
    obj: Any,
    event_data: UpdatedEventData | None,
    object_type: str,
    object_id: int,
) -> dict[str, Any]:
    # Build base nodes
    nodes = [text("updated ")]

    # Add field changes if available
    if event_data and event_data.changes:
        nodes.append(text(": "))
        changes = []

        for field_name, field_change in event_data.changes.items():
            display_name = field_name.replace("_", " ").title()
            old_str = "None" if field_change.old is None else str(field_change.old)
            new_str = "None" if field_change.new is None else str(field_change.new)
            changes.append(f"{display_name}: {old_str} → {new_str}")

        if changes:
            # Add first change with bold field name
            first_change = changes[0]
            parts = first_change.split(": ", 1)
            if len(parts) == 2:
                nodes.extend([bold(parts[0]), text(f": {parts[1]}")])
            else:
                nodes.append(text(first_change))

            # Add remaining changes
            for change in changes[1:]:
                parts = change.split(": ", 1)
                if len(parts) == 2:
                    nodes.extend([text(", "), bold(parts[0]), text(f": {parts[1]}")])
                else:
                    nodes.append(text(f", {change}"))

    return doc(paragraph(*nodes))


# ============================================================================
# Thread Message Consumers (one per event type for all threadable models)
# ============================================================================


# List of all threadable models
THREADABLE_MODELS = [Brand, Campaign, DeliverableMedia, Roster]


def _get_campaign_id(obj: Any) -> int | None:
    """Extract campaign_id from object (campaigns use their own ID)."""
    if isinstance(obj, Campaign):
        return obj.id
    if isinstance(obj, DeliverableMedia):
        # DeliverableMedia gets campaign_id from its deliverable
        return getattr(obj.deliverable, "campaign_id", None) if obj.deliverable else None
    return getattr(obj, "campaign_id", None)


@event_consumer(EventType.CREATED, model=THREADABLE_MODELS)
async def post_created_to_thread(session: AsyncSession, event: Event, obj: Any, channels: ChannelsPlugin) -> None:
    """Post creation events to thread (attributed to actor)."""
    object_ref = _format_object_ref(event, obj)

    # Simple creation message - no actor name needed since it's attributed to the user
    content = doc(paragraph(text("created "), bold(object_ref)))

    campaign_id = _get_campaign_id(obj)
    await _post_to_thread(
        session,
        event,
        content,
        user_id=event.actor_id,
        channels=channels,
        campaign_id=campaign_id,
    )


@event_consumer(EventType.UPDATED, model=THREADABLE_MODELS)
async def post_updated_to_thread(
    session: AsyncSession, event: Event, obj: BaseDBModel, channels: ChannelsPlugin
) -> None:
    """Post update events to thread (attributed to actor)."""
    # Parse event data into structured format
    event_data = _parse_event_data_to_updated(event.event_data)

    # Build message content
    content = build_update_message_content(
        obj=obj,
        event_data=event_data,
        object_type=event.object_type,
        object_id=event.object_id,
    )

    campaign_id = _get_campaign_id(obj)
    await _post_to_thread(
        session,
        event,
        content,
        user_id=event.actor_id,
        channels=channels,
        campaign_id=campaign_id,
    )


@event_consumer(EventType.DELETED, model=THREADABLE_MODELS)
async def post_deleted_to_thread(session: AsyncSession, event: Event, obj: Any, channels: ChannelsPlugin) -> None:
    """Post deletion events to thread (system message)."""
    object_ref = _format_object_ref(event, obj)

    # Deletion is a system message (no user attribution)
    content = doc(paragraph(text("deleted "), bold(object_ref)))

    campaign_id = _get_campaign_id(obj)
    await _post_to_thread(
        session,
        event,
        content,
        user_id=None,
        channels=channels,
        campaign_id=campaign_id,
    )


@event_consumer(EventType.STATE_CHANGED, model=THREADABLE_MODELS)
async def post_state_changed_to_thread(session: AsyncSession, event: Event, obj: Any, channels: ChannelsPlugin) -> None:
    """Post state change events to thread (system message)."""
    object_ref = _format_object_ref(event, obj)

    # Extract state change from event data
    if event.event_data and "state" in event.event_data:
        state_change = event.event_data["state"]
        old_state = state_change.get("old", "unknown").replace("_", " ").title()
        new_state = state_change.get("new", "unknown").replace("_", " ").title()

        content = doc(
            paragraph(
                text("moved "),
                bold(object_ref),
                text(" to "),
                bold(new_state),
                text(f" (from {old_state})"),
            )
        )
    else:
        # Fallback
        content = doc(paragraph(text("changed state of "), bold(object_ref)))

    campaign_id = _get_campaign_id(obj)
    await _post_to_thread(
        session,
        event,
        content,
        user_id=None,
        channels=channels,
        campaign_id=campaign_id,
    )
