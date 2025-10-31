"""Typed schemas for event_data payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def make_field_changes(old_values: dict[str, Any], new_values: dict[str, Any]) -> dict[str, FieldChange]:
    """
    Create a dict of FieldChange objects by comparing old and new values.

    Only includes fields that actually changed.

    Args:
        old_values: Dictionary of field names to old values
        new_values: Dictionary of field names to new values

    Returns:
        Dictionary of field names to FieldChange objects

    Example:
        >>> old = {"name": "Old Name", "status": "draft", "budget": 1000}
        >>> new = {"name": "New Name", "status": "draft", "budget": 2000}
        >>> changes = make_field_changes(old, new)
        >>> # Returns: {"name": FieldChange(old="Old Name", new="New Name"), "budget": FieldChange(old=1000, new=2000)}
    """
    changes = {}
    for field in old_values:
        if field in new_values and old_values[field] != new_values[field]:
            changes[field] = FieldChange(old=old_values[field], new=new_values[field])
    return changes


@dataclass
class FieldChange:
    """Represents a change to a single field."""

    old: Any
    new: Any


@dataclass
class UpdatedEventData:
    """Event data for UPDATED events.

    Contains a mapping of field names to their old/new values.

    Example:
        {
            "name": {"old": "Old Name", "new": "New Name"},
            "status": {"old": "draft", "new": "active"}
        }
    """

    changes: dict[str, FieldChange]


@dataclass
class StateChangedEventData:
    """Event data for STATE_CHANGED events.

    Tracks state transitions with optional metadata.

    Example:
        {
            "state": {"old": "draft", "new": "active"},
            "reason": "Approved by manager"
        }
    """

    state: FieldChange
    reason: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class CreatedEventData:
    """Event data for CREATED events.

    Contains initial values of key fields at creation time.

    Example:
        {
            "name": "Campaign Name",
            "status": "draft",
            "budget": 10000
        }
    """

    initial_values: dict[str, Any]


@dataclass
class DeletedEventData:
    """Event data for DELETED events.

    Contains final values of key fields before deletion.

    Example:
        {
            "name": "Campaign Name",
            "status": "archived",
            "deleted_reason": "No longer needed"
        }
    """

    final_values: dict[str, Any]
    reason: str | None = None


@dataclass
class CustomEventData:
    """Event data for CUSTOM events.

    Flexible structure for custom event types.

    Example:
        {
            "action": "email_sent",
            "payload": {"recipient": "user@example.com", "template": "welcome"}
        }
    """

    action: str
    payload: dict[str, Any] | None = None
