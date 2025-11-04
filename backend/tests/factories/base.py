"""Base factory configuration for polyfactory."""

from typing import Any

from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.models import BaseDBModel


class AsyncSessionPersistence:
    """Async persistence handler that properly saves to database."""

    def __init__(self, session: AsyncSession):
        """Initialize with async session."""
        self.session = session

    async def save(self, data: Any) -> Any:
        """Save a single instance to the database."""
        self.session.add(data)
        await self.session.flush()  # Flush to get IDs without committing
        await self.session.refresh(data)  # Refresh to get all attributes
        return data

    async def save_many(self, data: list[Any]) -> list[Any]:
        """Save multiple instances to the database."""
        for item in data:
            self.session.add(item)
        await self.session.flush()
        for item in data:
            await self.session.refresh(item)
        return data


class BaseFactory[T: BaseDBModel](SQLAlchemyFactory[T]):
    """Base factory for all database models."""

    __is_base_factory__ = True
    __faker__ = Faker()
    __session__ = None  # Will be set at runtime
    __check_model__ = False
    __set_relationships__ = False
    __set_association_proxy__ = False

    @classmethod
    async def create_async(cls, session: AsyncSession, **kwargs: Any) -> T:
        """Build and persist a single model instance asynchronously."""
        # Build the instance
        instance = cls.build(**kwargs)

        # Add to session and flush
        session.add(instance)
        await session.flush()
        await session.refresh(instance)

        return instance

    @classmethod
    async def create_batch_async(cls, session: AsyncSession, size: int, **kwargs: Any) -> list[T]:
        """Build and persist multiple model instances asynchronously."""
        instances = [cls.build(**kwargs) for _ in range(size)]

        # Add all to session and flush
        for instance in instances:
            session.add(instance)
        await session.flush()
        for instance in instances:
            await session.refresh(instance)

        return instances
