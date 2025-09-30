from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Sequence, Type, ClassVar, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, select, or_, inspect
import sqlalchemy as sa
from sqlalchemy.sql.base import ExecutableOption
from app.base.models import BaseDBModel
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ActionDTO,
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ColumnDefinitionDTO,
    SortDirection,
)
from app.objects.services import apply_filter

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
            raise ValueError(
                f"Unknown object type: {object_type}, needed: {cls._registry.keys()}"
            )
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

    # Subclasses must set these to register with the framework
    object_type: ClassVar[ObjectTypes]
    model: ClassVar[Type[BaseDBModel]]
    column_definitions: ClassVar[List[ColumnDefinitionDTO]]

    def __init_subclass__(cls, **kwargs):
        """Auto-register subclasses in the registry."""
        super().__init_subclass__(**kwargs)
        if cls.object_type is not None:
            ObjectRegistry.register(cls.object_type, cls)

    @classmethod
    @abstractmethod
    def to_detail_dto(cls, object: BaseDBModel) -> ObjectDetailDTO:
        """Convert to detailed DTO representation."""
        ...

    @classmethod
    @abstractmethod
    def to_list_dto(cls, object: BaseDBModel) -> ObjectListDTO:
        """Convert to list DTO representation."""
        ...

    @classmethod
    def get_load_options(cls) -> List[ExecutableOption]:
        """Return load options for eager loading. Override in subclasses."""
        return []

    @classmethod
    def create_search_filter(cls, search_term: str | None):
        """Create a search filter across all text fields in the model.

        Returns None if search_term is empty/None (short-circuit for performance).
        Otherwise returns an OR condition with ILIKE across all string columns.
        """
        # Short-circuit if no search term or empty/whitespace
        if not search_term or not search_term.strip():
            return None

        # Introspect model to find all string/text columns
        mapper = inspect(cls.model)
        conditions = []

        for column in mapper.columns:
            # Check if column is a string type
            if isinstance(column.type, (sa.String, sa.Text)):
                # Add ILIKE condition for case-insensitive search
                conditions.append(column.ilike(f"%{search_term}%"))

        # Return OR condition if we have any conditions
        return or_(*conditions) if conditions else None

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        """Apply list request filters/sorting to create database query."""
        query = select(cls.model)

        # Apply load options (eager loading, etc.)
        query = query.options(*cls.get_load_options())

        # Apply search filter if provided
        search_filter = cls.create_search_filter(request.search)
        if search_filter is not None:
            query = query.where(search_filter)

        # Apply structured filters and sorts using helper method
        query = cls.apply_request_to_query(query, cls.model, request)

        # Default sort if no sorts applied
        if not request.sorts:
            query = query.order_by(cls.model.created_at.desc())

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> BaseDBModel:
        query = (
            select(cls.model)
            .where(cls.model.id == object_id)
            .options(*cls.get_load_options())
        )

        result = await session.execute(query)
        obj = result.scalar_one_or_none()
        if not obj:
            raise ValueError(f"{cls.model.__name__} with id {object_id} not found")
        return obj

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[BaseDBModel], int]:
        """Get list of objects based on request parameters."""
        from sqlalchemy import select, func

        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        objects = result.scalars().all()

        return objects, total

    @classmethod
    def apply_request_to_query(
        cls, query: Select, model_class: Type[BaseDBModel], request: ObjectListRequest
    ) -> Select:
        """Helper method to apply filters and sorts from request to query."""
        # Apply structured filters
        if request.filters:
            for filter_def in request.filters:
                query = apply_filter(query, model_class, filter_def)

        # Apply structured sorts
        if request.sorts:
            for sort_def in request.sorts:
                column = getattr(model_class, sort_def.column, None)
                if column:
                    if sort_def.direction == SortDirection.sort_asc:
                        query = query.order_by(column.asc())
                    else:
                        query = query.order_by(column.desc())

        return query

    @classmethod
    def get_list_actions(cls) -> list[ActionDTO]:
        """Return list actions available for this object type."""
        return [
            ActionDTO(action="download", label="Download CSV", is_bulk_allowed=False),
            ActionDTO(action="save", label="Save view", is_bulk_allowed=False),
        ]
