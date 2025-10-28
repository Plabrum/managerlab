from sqlalchemy import select, func
from abc import ABC
from typing import Sequence, Type, ClassVar, List, TYPE_CHECKING, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, or_, inspect
import sqlalchemy as sa
from sqlalchemy.sql.base import ExecutableOption
from app.base.models import BaseDBModel
from app.base.registry import BaseRegistry
from app.objects.enums import ObjectTypes, FieldType
from app.objects.schemas import (
    ObjectListDTO,
    ObjectListRequest,
    ColumnDefinitionDTO,
    SortDirection,
    ObjectFieldDTO,
    StringFieldValue,
    IntFieldValue,
    FloatFieldValue,
    BoolFieldValue,
    EnumFieldValue,
    DateFieldValue,
    DatetimeFieldValue,
    USDFieldValue,
    EmailFieldValue,
    URLFieldValue,
    TextFieldValue,
    ImageFieldValue,
)
from app.objects.services import apply_filter
from app.utils.sqids import sqid_encode

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
    registry: ClassVar["ObjectRegistry"]

    # Optional overrides for title/subtitle generation
    title_field: ClassVar[str | None] = None
    subtitle_field: ClassVar[str | None] = None
    state_field: ClassVar[str] = "state"  # Default to "state" attribute

    # Action groups
    top_level_action_group: ClassVar["ActionGroupType | None"] = None
    action_group: ClassVar["ActionGroupType | None"] = None

    # Load options for eager loading relationships
    load_options: ClassVar[List[ExecutableOption]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.object_type is not None:
            cls.registry = ObjectRegistry()  # Store reference to singleton
            cls.registry.register(cls.object_type, cls)

    @classmethod
    def get_custom_fields(cls, obj: BaseDBModel) -> List[ObjectFieldDTO]:
        """Override to add custom fields not defined in column_definitions.

        Useful for computed fields, conditional fields, or fields that need
        complex logic beyond simple attribute access.

        Returns:
            List of additional ObjectFieldDTO instances to include in the list view
        """
        return []

    @classmethod
    def get_top_level_actions(cls) -> List["Any"]:
        """Get top-level actions for this object type (e.g., create).

        Returns:
            List of ActionDTO instances, or empty list if no top-level actions exist
        """
        if not cls.top_level_action_group:
            return []

        from app.actions.registry import ActionRegistry

        action_group = ActionRegistry().get_class(cls.top_level_action_group)
        return action_group.get_available_actions()

    @classmethod
    def _get_field_value(cls, obj: BaseDBModel, col_def: ColumnDefinitionDTO) -> Any:
        """Extract field value from object using accessor or key."""
        # Use accessor if provided, otherwise use key
        if col_def.accessor is not None:
            if callable(col_def.accessor):
                value = col_def.accessor(obj)
            else:
                value = getattr(obj, col_def.accessor, None)
        else:
            value = getattr(obj, col_def.key, None)

        # Apply formatter if provided
        if col_def.formatter is not None and value is not None:
            value = col_def.formatter(value)

        return value

    @classmethod
    def _create_field_value_wrapper(cls, value: Any, field_type: FieldType):
        """Wrap raw value in appropriate FieldValue type based on FieldType."""
        if value is None:
            return None

        match field_type:
            case FieldType.String:
                return StringFieldValue(value=str(value))
            case FieldType.Int:
                return IntFieldValue(value=int(value))
            case FieldType.Float:
                return FloatFieldValue(value=float(value))
            case FieldType.Bool:
                return BoolFieldValue(value=bool(value))
            case FieldType.Enum:
                return EnumFieldValue(value=str(value))
            case FieldType.Date:
                return DateFieldValue(value=value)
            case FieldType.Datetime:
                return DatetimeFieldValue(value=value)
            case FieldType.USD:
                return USDFieldValue(value=float(value))
            case FieldType.Email:
                return EmailFieldValue(value=str(value))
            case FieldType.URL:
                return URLFieldValue(value=str(value))
            case FieldType.Text:
                return TextFieldValue(value=value)
            case FieldType.Image:
                # Image values should be dicts with url and thumbnail_url
                if isinstance(value, dict):
                    return ImageFieldValue(**value)
                else:
                    return ImageFieldValue(url=str(value))
            case _:
                return StringFieldValue(value=str(value))

    @classmethod
    def to_list_dto(cls, obj: BaseDBModel) -> ObjectListDTO:
        """Auto-generate ObjectListDTO from column_definitions.

        This default implementation generates fields from column_definitions
        and can be extended via get_custom_fields() for special cases.
        """
        # Generate fields from column_definitions
        fields: List[ObjectFieldDTO] = []

        for col_def in cls.column_definitions:
            # Skip if not included in list view
            if not col_def.include_in_list:
                continue

            # Extract value
            value = cls._get_field_value(obj, col_def)

            # Skip None values unless nullable
            if value is None and not col_def.nullable:
                continue

            # Wrap value in appropriate type
            wrapped_value = cls._create_field_value_wrapper(value, col_def.type)

            # Create field DTO
            field_dto = ObjectFieldDTO(
                key=col_def.key,
                value=wrapped_value,
                label=col_def.label,
                editable=col_def.editable,
            )
            fields.append(field_dto)

        # Add custom fields
        fields.extend(cls.get_custom_fields(obj))

        # Get title and subtitle
        title = (
            cls._get_field_value(
                obj,
                next(
                    (
                        col
                        for col in cls.column_definitions
                        if col.key == cls.title_field
                    ),
                    cls.column_definitions[0],  # Fallback to first column
                ),
            )
            if cls.title_field
            else str(getattr(obj, cls.title_field or "name", ""))
        )

        subtitle = None
        if cls.subtitle_field:
            subtitle = str(getattr(obj, cls.subtitle_field, None))

        # Get per-object actions if action group is defined
        actions = []
        if cls.action_group:
            # Import here to avoid circular dependency
            from app.actions.registry import ActionRegistry

            action_group = ActionRegistry().get_class(cls.action_group)
            actions = action_group.get_available_actions(obj=obj)

        return ObjectListDTO(
            id=sqid_encode(obj.id),
            object_type=cls.object_type,
            title=str(title),
            subtitle=subtitle,
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
        """Build query from request filters, sorts, and search.

        Scope and soft-delete filtering are applied automatically via SQLAlchemy events.
        """
        query = select(cls.model)

        # Apply load options (eager loading, etc.)
        query = query.options(*cls.load_options)

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
        """Get object by ID.

        Scope and soft-delete filtering are applied automatically via SQLAlchemy events.
        """
        query = (
            select(cls.model)
            .where(cls.model.id == object_id)
            .options(*cls.load_options)
        )

        result = await session.execute(query)
        obj = result.unique().scalar_one_or_none()
        if not obj:
            raise ValueError(f"{cls.model.__name__} with id {object_id} not found")
        return obj

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[BaseDBModel], int]:
        """Get list of objects with filtering and pagination.

        Scope and soft-delete filtering are applied automatically via SQLAlchemy events.
        """
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        objects = result.unique().scalars().all()

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

    @classmethod
    def get_field_metadata(cls, field_name: str) -> ColumnDefinitionDTO | None:
        """Get column definition metadata for a field.

        Args:
            field_name: Name of the field to look up

        Returns:
            ColumnDefinitionDTO if field exists, None otherwise
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
            raise ValueError(
                f"Field '{field_name}' not found in {cls.object_type} column definitions"
            )
