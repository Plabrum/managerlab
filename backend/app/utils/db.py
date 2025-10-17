"""Database utility functions for common operations."""

from litestar.exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession


async def get_or_404[T](session: AsyncSession, model_class: type[T], id: int) -> T:
    """Get an entity by ID or raise a 404 exception."""
    entity = await session.get(model_class, id)
    if not entity:
        raise NotFoundException(detail="Not found")
    return entity


def update_model[T](model_instance: T, update_vals) -> T:
    """Update a model instance from a DTO/struct."""
    for field, value in update_vals.__dict__.items():
        if hasattr(model_instance, field):
            setattr(model_instance, field, value)
    return model_instance


def create_model[T](model_class: type[T], create_vals) -> T:
    """Create a new model instance from a DTO/struct."""
    data = {
        field: value
        for field, value in create_vals.__dict__.items()
        if value is not None
    }
    return model_class(**data)
