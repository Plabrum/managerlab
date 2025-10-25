"""Event emission service - pure event recording with consumer triggering."""

import logging
from dataclasses import asdict
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.base.models import BaseDBModel
from app.events.models import Event, EventType
from app.events.registry import trigger_consumers
from app.events.schemas import (
    CreatedEventData,
    UpdatedEventData,
    DeletedEventData,
    StateChangedEventData,
    CustomEventData,
)

logger = logging.getLogger(__name__)
type EventDataTypes = (
    CreatedEventData
    | UpdatedEventData
    | DeletedEventData
    | StateChangedEventData
    | CustomEventData
    | dict[str, Any]
    | None
)


async def emit_event(
    session: AsyncSession,
    event_type: EventType,
    obj: BaseDBModel,
    user_id: int,
    team_id: int,
    event_data: EventDataTypes = None,
) -> Event:
    # Get object metadata
    object_type = obj.__tablename__
    object_id = obj.id

    # Convert dataclass to dict if needed
    data_dict: dict[str, Any] | None = None
    if event_data is not None:
        if isinstance(event_data, dict):
            data_dict = event_data
        else:
            # Convert dataclass to dict
            data_dict = asdict(event_data)

    # Create Event record
    event = Event(
        actor_id=user_id,
        object_type=object_type,
        object_id=object_id,
        event_type=event_type,
        event_data=data_dict,
        team_id=team_id,
    )
    session.add(event)
    await session.flush()

    logger.info(
        f"Event emitted: {event_type.value} on {object_type}#{object_id} by User#{user_id}"
    )

    # Trigger consumers, passing the actual object
    await trigger_consumers(session, event, obj)

    return event
