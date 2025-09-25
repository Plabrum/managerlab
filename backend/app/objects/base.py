"""Base objects framework with auto-registration."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Type, ClassVar
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.types import ObjectTypes
from app.objects.schemas import ObjectDetailDTO, ObjectListDTO, ObjectListRequest

if TYPE_CHECKING:
    pass


class ObjectRegistry:
    """Registry mapping ObjectTypes to their corresponding classes."""

    _registry: Dict[ObjectTypes, Type["BaseObject"]] = {}

    @classmethod
    def register(cls, object_type: ObjectTypes, object_class: Type["BaseObject"]):
        """Register an object type with its class."""
        cls._registry[object_type] = object_class

    @classmethod
    def get_class(cls, object_type: ObjectTypes) -> Type["BaseObject"]:
        """Get the class for an object type."""
        if object_type not in cls._registry:
            raise ValueError(f"Unknown object type: {object_type}")
        return cls._registry[object_type]

    @classmethod
    def get_all_types(cls) -> Dict[ObjectTypes, Type["BaseObject"]]:
        """Get all registered object types."""
        return cls._registry.copy()

    @classmethod
    def is_registered(cls, object_type: ObjectTypes) -> bool:
        """Check if an object type is registered."""
        return object_type in cls._registry


class BaseObject(ABC):
    """Base class for all objects that participate in the objects framework."""

    # Subclasses must set this to register with the framework
    object_type: ClassVar[ObjectTypes] = None

    def __init_subclass__(cls, **kwargs):
        """Auto-register subclasses in the registry."""
        super().__init_subclass__(**kwargs)
        if cls.object_type is not None:
            ObjectRegistry.register(cls.object_type, cls)

    @abstractmethod
    async def to_detail_dto(
        self, session: AsyncSession, user_id: int | None = None
    ) -> ObjectDetailDTO:
        """Convert to detailed DTO representation."""
        pass

    @abstractmethod
    async def to_list_dto(
        self, session: AsyncSession, user_id: int | None = None
    ) -> ObjectListDTO:
        """Convert to list DTO representation."""
        pass

    @classmethod
    @abstractmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        """Apply list request filters/sorting to create database query."""
        pass

    @classmethod
    @abstractmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int):
        """Get object by ID."""
        pass
