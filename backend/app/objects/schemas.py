"""Object schemas and DTOs."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from app.base.schemas import BaseSchema
from app.objects.enums import FieldType, FilterType, SortDirection


class TextFilterDefinition(BaseSchema, tag=FilterType.text.value):
    """Text-based filter definition."""

    column: str
    operation: Literal["contains", "starts_with", "ends_with", "equals"]
    value: str


class RangeFilterDefinition(BaseSchema, tag=FilterType.range.value):
    """Range-based filter definition for numbers."""

    column: str
    start: Union[int, float, None] = None  # nullable start value
    finish: Union[int, float, None] = None  # nullable finish value


class DateFilterDefinition(BaseSchema, tag=FilterType.date.value):
    """Date-based filter definition."""

    column: str
    start: datetime | None = None
    finish: datetime | None = None


class BooleanFilterDefinition(BaseSchema, tag=FilterType.boolean.value):
    """Boolean-based filter definition."""

    column: str
    value: bool  # true or false


FilterDefinition = Union[
    TextFilterDefinition,
    RangeFilterDefinition,
    DateFilterDefinition,
    BooleanFilterDefinition,
]


class SortDefinition(BaseSchema):
    """Definition of a sort to apply."""

    column: str
    direction: SortDirection


class ObjectFieldDTO(BaseSchema):
    """DTO for object field representation."""

    key: str
    value: Any
    type: FieldType
    label: Optional[str] = None
    editable: bool = True


class ColumnDefinitionDTO(BaseSchema):
    """Definition of a column for list views."""

    key: str
    label: str
    type: FieldType
    sortable: bool = True
    available_filters: List[FilterType] = []
    default_visible: bool = True


class ActionDTO(BaseSchema):
    """DTO for action representation."""

    action: str
    label: str
    available: bool = True
    priority: int = 100


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
    fields: List[ObjectFieldDTO]
    actions: List[ActionDTO]
    created_at: str
    updated_at: str
    children: List[Dict[str, ObjectRelationDTO]] = []
    parents: List[Dict[str, ObjectRelationDTO]] = []


class ObjectListDTO(BaseSchema):
    """Lightweight object representation for lists/tables."""

    id: str
    object_type: str
    title: str
    state: str
    created_at: str
    updated_at: str
    subtitle: Optional[str] = None
    actions: List[ActionDTO] = []
    fields: List[ObjectFieldDTO] = []


class ObjectListRequest(BaseSchema):
    """Request schema for listing objects."""

    limit: int = 50
    offset: int = 0
    filters: List[FilterDefinition] = []
    sorts: List[SortDefinition] = []


class ObjectListResponse(BaseSchema):
    """Response schema for object lists."""

    objects: List[ObjectListDTO]
    total: int
    limit: int
    offset: int
    columns: List[ColumnDefinitionDTO]
