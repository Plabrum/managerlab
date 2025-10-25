# Events Platform - Implementation Guide

## Overview

A clean, event-driven architecture for tracking object lifecycle changes. Events are:
- **Team-scoped** for data isolation via RLS
- **Pure event records** - no side effects in emission
- **Consumer-driven** - downstream actions handled by registered consumers
- **Structured data** - single JSONB field for flexible event data

## Architecture

### Event Flow
```
emit_event() → Record Event → Trigger Consumers → Downstream Actions
                  ↓                                     ↓
              events table                    - Thread messages
                                              - Notifications
                                              - Webhooks
                                              - Analytics
```

## What Was Built

### 1. Core Models (`backend/app/events/models.py`)
- **Event**: Append-only log table with team-scoped RLS
- **EventType**: Enum for event categories (CREATED, UPDATED, DELETED, STATE_CHANGED)
- Optimized indexes for:
  - Team-wide event feeds
  - Object-specific timelines
  - Actor-specific events

### 2. Event Service (`backend/app/events/service.py`)
Pure event emission:
- **`emit_event()`** - Records event and triggers consumers (no side effects)

### 3. Consumer Registry (`backend/app/events/registry.py`)
Decorator-based consumer registration:
- **`@event_consumer()`** - Register functions to handle events
- **`trigger_consumers()`** - Synchronously execute all registered consumers

### 4. Event Consumers (`backend/app/events/consumers.py`)
Example consumers:
- **`post_to_thread()`** - Posts events as messages to object threads

### 5. Typed Event Schemas (`backend/app/events/schemas.py`)
Type-safe msgspec structs for event data:
- **`CreatedEventData`** - Initial values at creation
- **`UpdatedEventData`** - Field changes with old/new values
- **`DeletedEventData`** - Final values before deletion
- **`StateChangedEventData`** - State transitions with reason
- **`CustomEventData`** - Flexible custom events
- **`FieldChange`** - Individual field change with old/new
- **`make_field_changes()`** - Helper to compute changes from old/new dicts

### 6. Database Migration
- `backend/alembic/versions/dae53f291868_rename_activity_events_to_events_and_.py`
- Renames `activity_events` → `events`
- Simplifies schema: single `event_data` JSONB field
- **Run `make db-migrate` to apply**

## Usage Examples

### Track Object Creation (Using Helper)

```python
from app.utils.db import create_model_with_event

# Create object and automatically emit CREATED event
campaign = await create_model_with_event(
    session=transaction,
    team_id=team_id,
    campaign_id=None,
    model_class=Campaign,
    create_vals=campaign_data,
    actor_id=request.user,
    track_fields=["name", "status", "budget"],  # Optional: specify which fields to track
)
# Object is automatically added, flushed, and event is emitted!
```

### Track Object Updates (Using Helper)

```python
from app.utils.db import update_model_with_event

# Update object and automatically emit UPDATED event (only if fields changed)
campaign = await update_model_with_event(
    session=transaction,
    model_instance=campaign,
    update_vals=update_data,
    actor_id=request.user,
    team_id=team_id,
    track_fields=["name", "status", "budget"],  # Optional: specify which fields to track
)
# Object is updated, flushed, changes are computed, and event is emitted!
```

### Track Object Creation (Manual)

```python
from app.events import emit_event, EventType, CreatedEventData

# Create the object
campaign = create_model(team_id, None, Campaign, data)
transaction.add(campaign)
await transaction.flush()

# Emit creation event with typed data
await emit_event(
    session=transaction,
    event_type=EventType.CREATED,
    obj=campaign,
    actor_id=request.user,
    team_id=team_id,
    event_data=CreatedEventData(
        initial_values={"name": campaign.name, "status": campaign.status}
    ),
)
```

### Track Object Updates (Manual)

```python
from app.events import emit_event, EventType, UpdatedEventData, make_field_changes

# Capture old values BEFORE updating
old_values = {"name": campaign.name, "status": campaign.status}

# Update the object
update_model(campaign, update_data)
await transaction.flush()

# Capture new values and compute changes
new_values = {"name": campaign.name, "status": campaign.status}
changes = make_field_changes(old_values, new_values)

# Emit update event with typed data
if changes:
    await emit_event(
        session=transaction,
        event_type=EventType.UPDATED,
        obj=campaign,
        actor_id=request.user,
        team_id=team_id,
        event_data=UpdatedEventData(changes=changes),
    )
```

### Track State Transitions

```python
from app.events import emit_event, EventType, StateChangedEventData, FieldChange

# Capture old state
old_state = campaign.state

# Update to new state
campaign.state = CampaignState.APPROVED
await transaction.flush()

# Emit state change event with typed data
if old_state != campaign.state:
    await emit_event(
        session=transaction,
        event_type=EventType.STATE_CHANGED,
        obj=campaign,
        actor_id=request.user,
        team_id=team_id,
        event_data=StateChangedEventData(
            state=FieldChange(old=old_state.name, new=campaign.state.name),
            reason="Approved by manager",
        ),
    )
```

### Track Deletions

```python
from app.events import emit_event, EventType, DeletedEventData

# Emit deletion event BEFORE soft-deleting
await emit_event(
    session=transaction,
    event_type=EventType.DELETED,
    obj=campaign,
    actor_id=request.user,
    team_id=team_id,
    event_data=DeletedEventData(
        final_values={"name": campaign.name, "status": campaign.status},
        reason="No longer needed",
    ),
)
campaign.soft_delete()
await transaction.flush()
```

### Using Raw Dicts (Backwards Compatible)

```python
from app.events import emit_event, EventType

# You can still use plain dicts if needed
await emit_event(
    session=transaction,
    event_type=EventType.UPDATED,
    obj=campaign,
    actor_id=request.user,
    team_id=team_id,
    event_data={"name": {"old": "Old", "new": "New"}},  # Plain dict still works
)
```

## Creating Event Consumers

Add custom downstream logic by creating consumers:

```python
from app.events.registry import event_consumer
from app.events.enums import EventType
from app.events.models import Event
from sqlalchemy.ext.asyncio import AsyncSession

@event_consumer(EventType.CREATED, EventType.UPDATED)
async def send_notification(session: AsyncSession, event: Event) -> None:
    """Send notification when objects are created or updated."""
    # Your notification logic here
    print(f"Event {event.event_type.value} on {event.object_type}#{event.object_id}")
```

Register consumers by importing them in `backend/app/events/consumers.py`.

## Accessing Events

Events can be accessed in multiple ways:

1. **In Thread Messages**: Events for threadable objects appear as system messages
2. **Via WebSocket**: Real-time updates when events occur
3. **Direct Database Query**: Query `Event` table for analytics/reports

## Next Steps

### 1. Apply Migration

```bash
make db-migrate
```

### 2. Add Tracking to Routes

Choose which operations to track by calling `emit_event()`:
- **Create operations**: After `transaction.flush()` on new objects
- **Update operations**: Capture old values, compute changes, emit
- **State changes**: Use `track_state_transition()` helper
- **Deletions**: Before calling `soft_delete()`
- **Custom events**: Domain-specific actions (approvals, payments, etc.)

### 3. View Activity in Threads

Activity events appear automatically in threads for threadable objects. No additional UI needed!

## Architecture Decisions

### Why No API Endpoints?

Activity events are accessed via:
- **Thread messages** (primary way users see activity)
- **Direct database queries** (when building reports/analytics)

Separate API endpoints would be redundant.

### Why Team-Scoped Only?

ActivityEvent is team-scoped (not campaign-scoped) because:
- Most objects are team-scoped (brands, roster, users)
- Campaigns are temporary, but activity log should persist
- Thread messages remain campaign-scoped for proper isolation

### Why Dual-Write?

Writing to both ActivityEvent and Thread messages provides:
- **Audit trail**: Permanent, queryable activity log
- **Real-time visibility**: Thread messages with WebSocket updates
- **Flexibility**: Can query ActivityEvent without loading threads

### Why Append-Only?

Activity events are never updated or deleted because:
- Provides immutable audit trail
- Simplifies querying (no need to handle updates)
- Matches regulatory/compliance requirements

## Troubleshooting

### Events Not Showing in Threads

Check that:
1. Object has `ThreadableMixin` in its model
2. Object has been flushed (has an ID) before calling `emit_event()`
3. WebSocket connection is active for real-time updates

### Field Changes Not Captured

Ensure you:
1. Call `capture_values()` BEFORE updating the object
2. Compute changes dict before calling `emit_event()`
3. Flush after updating but before emitting event

### RLS Issues

Verify:
1. `team_id` is set correctly in request session
2. Database RLS policies are enabled (run migration)
3. User has access to the team

## Files Created/Modified

### New Files
- `backend/app/events/__init__.py`
- `backend/app/events/models.py`
- `backend/app/events/enums.py`
- `backend/app/events/service.py`
- `backend/app/events/schemas.py` - **NEW**: Typed event data schemas
- `backend/app/events/registry.py`
- `backend/app/events/consumers.py`
- `backend/alembic/versions/2fe5f8d99202_add_activity_events_table.py`

### Modified Files
- `backend/app/utils/db.py` - Added event tracking helpers:
  - `create_model_with_event()` - Create model and emit CREATED event
  - `update_model_with_event()` - Update model and emit UPDATED event

---

**Philosophy**: Keep it simple. One function (`emit_event()`) for all tracking. Access via threads. No API overhead.
