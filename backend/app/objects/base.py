from sqlalchemy import select, func
from abc import ABC, abstractmethod
from typing import Sequence, Type, ClassVar, List, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, or_, inspect
import sqlalchemy as sa
from sqlalchemy.sql.base import ExecutableOption
from app.base.models import BaseDBModel
from app.base.registry import BaseRegistry
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ColumnDefinitionDTO,
    SortDirection,
)
from app.objects.services import apply_filter

if TYPE_CHECKING:
    from app.actions.enums import ActionGroupType


class ObjectRegistry(
    BaseRegistry[ObjectTypes, Type["BaseObject"]],
):
    pass


class BaseObject(ABC):
    object_type: ClassVar[ObjectTypes]
    model: ClassVar[Type[BaseDBModel]]
    column_definitions: ClassVar[List[ColumnDefinitionDTO]]
    registry: ClassVar["ObjectRegistry | None"] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.object_type is not None:
            cls.registry = ObjectRegistry()  # Store reference to singleton
            cls.registry.register(cls.object_type, cls)

    @classmethod
    @abstractmethod
    async def to_detail_dto(cls, object: BaseDBModel) -> ObjectDetailDTO: ...

    @classmethod
    @abstractmethod
    def to_list_dto(cls, object: BaseDBModel) -> ObjectListDTO: ...

    @classmethod
    def get_top_level_action_group(cls) -> "ActionGroupType | None":
        """Return the ActionGroupType for top-level actions (e.g., create) for this object.

        Override this method to specify which action group contains top-level actions
        like 'create' that should be displayed in the list view.

        Returns:
            ActionGroupType for top-level actions, or None if no top-level actions exist
        """
        return None

    @classmethod
    def get_load_options(cls) -> List[ExecutableOption]:
        return []

    @classmethod
    def create_search_filter(cls, search_term: str | None):
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
