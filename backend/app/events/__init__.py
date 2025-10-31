"""Events domain module for object lifecycle tracking."""

# Import consumers to register them
from app.events import consumers  # noqa: F401
from app.events.models import Event, EventType
from app.events.schemas import (
    CreatedEventData,
    CustomEventData,
    DeletedEventData,
    FieldChange,
    StateChangedEventData,
    UpdatedEventData,
    make_field_changes,
)
from app.events.service import emit_event

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
