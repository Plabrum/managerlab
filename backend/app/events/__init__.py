"""Events domain module for object lifecycle tracking."""

from app.events.models import Event, EventType
from app.events.service import emit_event
from app.events.schemas import (
    CreatedEventData,
    UpdatedEventData,
    DeletedEventData,
    StateChangedEventData,
    CustomEventData,
    FieldChange,
    make_field_changes,
)

# Import consumers to register them
from app.events import consumers  # noqa: F401

__all__ = [
    "Event",
    "EventType",
    "emit_event",
    "CreatedEventData",
    "UpdatedEventData",
    "DeletedEventData",
    "StateChangedEventData",
    "CustomEventData",
    "FieldChange",
    "make_field_changes",
]
