"""Object schemas and DTOs."""

from datetime import date, datetime
from typing import Dict, List, Literal, Optional, Union

from app.base.schemas import BaseSchema
from app.objects.enums import FieldType, FilterType, SortDirection
from app.actions.schemas import ActionDTO


class TextFilterDefinition(BaseSchema, tag=FilterType.text_filter.value):
    """Text-based filter definition."""

    column: str
    operation: Literal["contains", "starts_with", "ends_with", "equals"]
    value: str


class RangeFilterDefinition(BaseSchema, tag=FilterType.range_filter.value):
    """Range-based filter definition for numbers."""

    column: str
    start: Union[int, float, None] = None  # nullable start value
    finish: Union[int, float, None] = None  # nullable finish value


class DateFilterDefinition(BaseSchema, tag=FilterType.date_filter.value):
    """Date-based filter definition."""

    column: str
    start: datetime | None = None
    finish: datetime | None = None


class BooleanFilterDefinition(BaseSchema, tag=FilterType.boolean_filter.value):
    """Boolean-based filter definition."""

    column: str
    value: bool  # true or false


class EnumFilterDefinition(BaseSchema, tag=FilterType.enum_filter.value):
    column: str
    values: List[str]  # list of selected enum values


FilterDefinition = Union[
    TextFilterDefinition,
    RangeFilterDefinition,
    DateFilterDefinition,
    BooleanFilterDefinition,
    EnumFilterDefinition,
]


class SortDefinition(BaseSchema):
    """Definition of a sort to apply."""

    column: str
    direction: SortDirection


# Field value types for discriminated union
class StringFieldValue(BaseSchema, tag=FieldType.String.value):
    """String field value."""

    value: str


class IntFieldValue(BaseSchema, tag=FieldType.Int.value):
    """Integer field value."""

    value: int


class FloatFieldValue(BaseSchema, tag=FieldType.Float.value):
    """Float field value."""

    value: float


class BoolFieldValue(BaseSchema, tag=FieldType.Bool.value):
    """Boolean field value."""

    value: bool


class EnumFieldValue(BaseSchema, tag=FieldType.Enum.value):
    """Enum field value."""

    value: str


class DateFieldValue(BaseSchema, tag=FieldType.Date.value):
    """Date field value."""

    value: date


class DatetimeFieldValue(BaseSchema, tag=FieldType.Datetime.value):
    """Datetime field value."""

    value: datetime


class USDFieldValue(BaseSchema, tag=FieldType.USD.value):
    """USD currency field value."""

    value: float


class EmailFieldValue(BaseSchema, tag=FieldType.Email.value):
    """Email field value."""

    value: str


class URLFieldValue(BaseSchema, tag=FieldType.URL.value):
    """URL field value."""

    value: str


class TextFieldValue(BaseSchema, tag=FieldType.Text.value):
    """Text field value (long-form text)."""

    value: str


class ImageFieldValue(BaseSchema, tag=FieldType.Image.value):
    """Image field with both full-size and thumbnail URLs.

    Future: Consider adding width, height, alt for better UX.
    """

    url: str
    thumbnail_url: str | None = None


# Union of all field value types
FieldValue = Union[
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
]


class ObjectFieldDTO(BaseSchema):
    """DTO for object field representation."""

    key: str
    value: FieldValue | None
    label: Optional[str] = None
    editable: bool = True


class ColumnDefinitionDTO(BaseSchema):
    """Definition of a column for list views."""

    key: str
    label: str
    type: FieldType
    filter_type: FilterType
    sortable: bool = True
    default_visible: bool = True
    available_values: List[str] | None = None


class ObjectRelationDTO(BaseSchema):
    """DTO for object relationships (parents/children)."""

    object_type: str
    sqid: str
    title: str


class ObjectDetailDTO(BaseSchema):
    """Detailed object representation."""

    id: str
    object_type: str
    state: str
    title: str
    fields: List[ObjectFieldDTO]
    actions: List[ActionDTO]
    created_at: datetime
    updated_at: datetime
    children: List[Dict[str, ObjectRelationDTO]] = []
    parents: List[Dict[str, ObjectRelationDTO]] = []


class ObjectListDTO(BaseSchema):
    """Lightweight object representation for lists/tables."""

    id: str
    object_type: str
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    subtitle: Optional[str] = None
    actions: List[ActionDTO] = []
    fields: List[ObjectFieldDTO] = []
    link: Optional[str] = None

    def __post_init__(self) -> None:
        self.link = f"{self.object_type}/{self.id}"


class ObjectListRequest(BaseSchema):
    """Request schema for listing objects."""

    limit: int = 50
    offset: int = 0
    filters: List[FilterDefinition] = []
    sorts: List[SortDefinition] = []
    search: str | None = None
    column: list[str] | None = None


class ObjectListResponse(BaseSchema):
    """Response schema for object lists."""

    objects: List[ObjectListDTO]
    total: int
    limit: int
    offset: int
    columns: List[ColumnDefinitionDTO]
    actions: list[ActionDTO] = []
