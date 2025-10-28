"""Event consumer registry with decorator-based registration and filtering."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.base.models import BaseDBModel
from app.base.registry import BaseRegistry
from app.events.enums import EventType
from app.events.models import Event

logger = logging.getLogger(__name__)

# Type alias for consumer functions
# Consumers receive: session, event, obj, and optionally other dependencies via DI
# Using Callable[..., Awaitable[None]] to allow flexible signatures
EventConsumer = Callable[..., Awaitable[None]]


@dataclass
class ConsumerRegistration:
    """Registration info for an event consumer."""

    consumer: EventConsumer
    model_filters: list[Type[BaseDBModel]] | None = None

    def matches(self, event: Event) -> bool:
        """Check if this consumer should handle the given event."""
        if self.model_filters is None:
            return True

        # Check if event's object_type matches any of the model table names
        return any(
            event.object_type == model.__tablename__ for model in self.model_filters
        )


class EventConsumerRegistry(BaseRegistry[EventType, list[ConsumerRegistration]]):
    """Registry for event consumers with filtering support."""

    def register_consumer(
        self,
        event_type: EventType,
        consumer: EventConsumer,
        model_filters: list[Type[BaseDBModel]] | None = None,
    ) -> None:
        """
        Register a consumer for an event type with optional model filtering.

        Args:
            event_type: The event type to listen for
            consumer: The consumer function to call
            model_filters: Optional list of model classes to filter by
        """
        if event_type not in self._registry:
            self._registry[event_type] = []

        registration = ConsumerRegistration(
            consumer=consumer, model_filters=model_filters
        )
        self._registry[event_type].append(registration)

        if model_filters:
            models_str = ", ".join(m.__tablename__ for m in model_filters)
            filter_info = f" (filtered to {models_str})"
        else:
            filter_info = ""
        logger.debug(
            f"Registered event consumer '{consumer.__name__}' for {event_type.value}{filter_info}"
        )

    def get_consumers(self, event: Event) -> list[EventConsumer]:
        """
        Get all consumers that should handle the given event.

        Applies model filtering to only return matching consumers.

        Args:
            event: The event to get consumers for

        Returns:
            List of consumer functions that match the event
        """
        registrations = self._registry.get(event.event_type, [])
        return [reg.consumer for reg in registrations if reg.matches(event)]


# Global singleton registry
_registry = EventConsumerRegistry()


def event_consumer(
    *event_types: EventType,
    model: Type[BaseDBModel] | list[Type[BaseDBModel]] | None = None,
) -> Callable[[EventConsumer], EventConsumer]:
    """
    Decorator to register a function as an event consumer.

    Consumer functions are called synchronously after an event is emitted.

    Args:
        *event_types: One or more EventType values to listen for
        model: Optional model class or list of model classes to filter events by

    Examples:
        # Handle all created events
        @event_consumer(EventType.CREATED)
        async def log_creation(session: AsyncSession, event: Event, obj: BaseDBModel) -> None:
            print(f"Created: {event.object_type}#{event.object_id}")

        # Handle only Brand creation
        @event_consumer(EventType.CREATED, model=Brand)
        async def notify_brand_creation(session: AsyncSession, event: Event, brand: Brand) -> None:
            print(f"Brand created: {brand.name}")

        # Handle multiple models
        @event_consumer(EventType.CREATED, model=[Brand, Campaign])
        async def notify_threadable_creation(session: AsyncSession, event: Event, obj: BaseDBModel) -> None:
            print(f"Threadable created: {obj.__tablename__}")

        # Handle multiple event types for a specific model
        @event_consumer(EventType.CREATED, EventType.UPDATED, model=Campaign)
        async def track_campaign_changes(session: AsyncSession, event: Event, campaign: Campaign) -> None:
            print(f"Campaign {event.event_type.value}: {campaign.name}")
    """

    def decorator(func: EventConsumer) -> EventConsumer:
        # Normalize model to list
        model_filters = None
        if model is not None:
            model_filters = [model] if not isinstance(model, list) else model

        for event_type in event_types:
            _registry.register_consumer(event_type, func, model_filters)
        return func

    return decorator


async def trigger_consumers(
    session: AsyncSession, event: Event, obj: BaseDBModel, **dependencies
) -> None:
    """
    Trigger all registered consumers for an event.

    Consumers are called synchronously in registration order.
    Failures in one consumer don't prevent others from running.

    Args:
        session: Database session
        event: The event that was emitted
        obj: The actual object that triggered the event
        **dependencies: Additional dependencies from DI (e.g., channels)
    """
    import inspect

    consumers = _registry.get_consumers(event)

    if not consumers:
        logger.debug(
            f"No consumers registered for {event.event_type.value} on {event.object_type}"
        )
        return

    logger.debug(
        f"Triggering {len(consumers)} consumer(s) for {event.event_type.value} on {event.object_type}#{event.object_id}"
    )

    for consumer in consumers:
        try:
            # Inspect consumer signature to pass only accepted parameters
            sig = inspect.signature(consumer)
            params = sig.parameters

            # Prepare candidate arguments (core + dependencies)
            candidate_args = {
                "session": session,
                "event": event,
                "obj": obj,
                **dependencies,
            }

            # Filter to only parameters the consumer accepts
            filtered_kwargs = {
                name: val for name, val in candidate_args.items() if name in params
            }

            await consumer(**filtered_kwargs)
            logger.debug(f"Consumer '{consumer.__name__}' completed successfully")
        except Exception as e:
            logger.error(
                f"Consumer '{consumer.__name__}' failed for event {event.id}: {e}",
                exc_info=True,
            )
            # Continue processing other consumers even if one fails


def get_registered_consumers() -> dict[EventType, list[str]]:
    """
    Get all registered consumers (for debugging/inspection).

    Returns:
        Dictionary mapping event types to consumer function names
    """
    return {
        event_type: [reg.consumer.__name__ for reg in registrations]
        for event_type, registrations in _registry.get_all_types().items()
    }
