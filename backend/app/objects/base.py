from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ClassVar

import sqlalchemy as sa
from sqlalchemy import Select, func, inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.actions.registry import ActionRegistry
from app.base.models import BaseDBModel
from app.base.registry import BaseRegistry
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ColumnDefinitionSchema,
    ObjectColumn,
    ObjectFieldDTO,
    ObjectListRequest,
    ObjectListSchema,
    SortDirection,
)
from app.objects.services import apply_filter, get_filter_by_field_type
from app.utils.sqids import sqid_encode

if TYPE_CHECKING:
    from app.actions.enums import ActionGroupType


class ObjectRegistry(
    BaseRegistry[ObjectTypes, type["BaseObject"]],
):
    pass


class BaseObject[O: BaseDBModel](ABC):
    object_type: ClassVar[ObjectTypes]
    column_definitions: ClassVar[list[ObjectColumn]]
    registry: ClassVar["ObjectRegistry"]

    @classmethod
    @abstractmethod
    def model(cls) -> type[O]: ...

    @classmethod
    @abstractmethod
    def title_field(cls, obj: O) -> str: ...

    @classmethod
    @abstractmethod
    def subtitle_field(cls, obj: O) -> str: ...

    @classmethod
    def state_field(cls, obj: O) -> str | None:
        return None

    # Action groups
    top_level_action_group: ClassVar["ActionGroupType | None"] = None
    action_group: ClassVar["ActionGroupType | None"] = None

    # Load options for eager loading relationships
    load_options: ClassVar[list[ExecutableOption]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.object_type is not None:
            cls.registry = ObjectRegistry()  # Store reference to singleton
            cls.registry.register(cls.object_type, cls)

    @classmethod
    def get_column_schemas(cls) -> list[ColumnDefinitionSchema]:
        return [
            ColumnDefinitionSchema(
                key=col.key,
                label=col.label,
                type=col.type,
                sortable=col.sortable,
                default_visible=col.default_visible,
                available_values=col.available_values,
                object_type=col.object_type,
                filter_type=get_filter_by_field_type(col.type),
            )
            for col in cls.column_definitions
        ]

    @classmethod
    def get_top_level_actions(cls) -> list["Any"]:
        if not cls.top_level_action_group:
            return []
        action_group = ActionRegistry().get_class(cls.top_level_action_group)
        return action_group.get_available_actions()

    @classmethod
    def to_list_schema(cls, obj: O) -> ObjectListSchema:
        # Generate fields from column_definitions
        fields: list[ObjectFieldDTO] = []

        for col_def in cls.column_definitions:
            # Skip if not included in list view
            if not col_def.include_in_list:
                continue

            # Extract already-wrapped field value from column definition
            field_value = col_def.value(obj)

            # Create field DTO
            field_dto = ObjectFieldDTO(
                key=col_def.key,
                value=field_value,
                label=col_def.label,
                editable=col_def.editable,
            )
            fields.append(field_dto)

        # Get per-object actions if action group is defined
        actions = []
        if cls.action_group:
            action_group = ActionRegistry().get_class(cls.action_group)
            actions = action_group.get_available_actions(obj=obj)

        return ObjectListSchema(
            id=sqid_encode(obj.id),
            object_type=cls.object_type,
            title=cls.title_field(obj),
            subtitle=cls.subtitle_field(obj),
            state=getattr(obj, "state", None),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            actions=actions,
            fields=fields,
        )

    @classmethod
    def create_search_filter(cls, search_term: str | None):
        # Short-circuit if no search term or empty/whitespace
        if not search_term or not search_term.strip():
            return None

        # Introspect model to find all string/text columns
        mapper = inspect(cls.model())
        conditions = []

        for column in mapper.columns:
            # Check if column is a string type
            if isinstance(column.type, sa.String | sa.Text):
                # Add ILIKE condition for case-insensitive search
                conditions.append(column.ilike(f"%{search_term}%"))

        # Return OR condition if we have any conditions
        return or_(*conditions) if conditions else None

    @classmethod
    async def query_from_request(cls, session: AsyncSession, request: ObjectListRequest):
        """Build query from request filters, sorts, and search.

        Scope and soft-delete filtering are applied automatically via SQLAlchemy events.
        """
        query = select(cls.model())

        # Apply load options (eager loading, etc.)
        query = query.options(*cls.load_options)

        # Apply search filter if provided
        search_filter = cls.create_search_filter(request.search)
        if search_filter is not None:
            query = query.where(search_filter)

        # Apply structured filters and sorts using helper method
        query = cls.apply_request_to_query(query, cls.model(), request)

        # Default sort if no sorts applied
        if not request.sorts:
            query = query.order_by(cls.model().created_at.desc())

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> BaseDBModel:
        """Get object by ID.

        Scope and soft-delete filtering are applied automatically via SQLAlchemy events.
        """
        query = select(cls.model()).where(cls.model().id == object_id).options(*cls.load_options)

        result = await session.execute(query)
        obj = result.unique().scalar_one_or_none()
        if not obj:
            raise ValueError(f"{cls.model.__name__} with id {object_id} not found")
        return obj

    @classmethod
    async def get_list(cls, session: AsyncSession, request: ObjectListRequest) -> tuple[Sequence[BaseDBModel], int]:
        """Get list of objects with filtering and pagination.

        Scope and soft-delete filtering are applied automatically via SQLAlchemy events.
        """
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(select(func.count()).select_from(query.subquery()))
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        objects = result.unique().scalars().all()

        return objects, total

    @classmethod
    def apply_request_to_query(
        cls, query: Select, model_class: type[BaseDBModel], request: ObjectListRequest
    ) -> Select:
        if request.filters:
            for filter_def in request.filters:
                query = apply_filter(query, model_class, filter_def)

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
    def get_field_metadata(cls, field_name: str) -> ObjectColumn | None:
        """Get column definition metadata for a field.

        Args:
            field_name: Name of the field to look up

        Returns:
            ObjectColumn if field exists, None otherwise
        """
        for col_def in cls.column_definitions:
            if col_def.key == field_name:
                return col_def
        return None

    @classmethod
    def validate_field_exists(cls, field_name: str) -> None:
        """Validate that a field exists in column definitions.

        Args:
            field_name: Name of the field to validate

        Raises:
            ValueError: If field does not exist
        """
        if cls.get_field_metadata(field_name) is None:
            raise ValueError(f"Field '{field_name}' not found in {cls.object_type} column definitions")
