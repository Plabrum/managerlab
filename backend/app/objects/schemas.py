"""Object schemas and DTOs."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal

from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
from app.client.s3_client import BaseS3Client
from app.media.models import Media
from app.objects.enums import (
    AggregationType,
    FieldType,
    FilterType,
    Granularity,
    ObjectTypes,
    RelationCardinality,
    RelationType,
    SortDirection,
    TimeRange,
)


class TextFilterDefinition(BaseSchema, tag=FilterType.text_filter.value):
    """Text-based filter definition."""

    column: str
    operation: Literal["contains", "starts_with", "ends_with", "equals"]
    value: str


class RangeFilterDefinition(BaseSchema, tag=FilterType.range_filter.value):
    """Range-based filter definition for numbers."""

    column: str
    start: int | float | None = None  # nullable start value
    finish: int | float | None = None  # nullable finish value


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
    values: list[str]  # list of selected enum values


class ObjectFilterDefinition(BaseSchema, tag=FilterType.object_filter.value):
    """Object reference filter definition."""

    column: str
    values: list[str]  # list of SQIDs to filter by


FilterDefinition = (
    TextFilterDefinition
    | RangeFilterDefinition
    | DateFilterDefinition
    | BooleanFilterDefinition
    | EnumFilterDefinition
    | ObjectFilterDefinition
)


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
    """URL field value with optional display label."""

    value: str
    label: str | None = None  # Display label for the URL (e.g., brand name)


class ObjectFieldValue(BaseSchema, tag=FieldType.Object.value):
    """Object reference field value with SQID and type information."""

    value: str  # SQID of the referenced object
    object_type: ObjectTypes  # Type of object being referenced
    label: str | None = None  # Display label for the object (e.g., brand name)


class TextFieldValue(BaseSchema, tag=FieldType.Text.value):
    """Text field value (long-form text)."""

    value: dict


class ImageFieldValue(BaseSchema, tag=FieldType.Image.value):
    """Image field with both full-size and thumbnail URLs.

    Future: Consider adding width, height, alt for better UX.
    """

    url: str
    thumbnail_url: str | None = None


def media_to_image_field_value(
    media: Media,
    s3_client: BaseS3Client,
):
    """Generate S3 presigned URLs for profile photo."""

    photo_url = s3_client.generate_presigned_download_url(key=media.file_key, expires_in=3600)
    thumbnail_url = (
        s3_client.generate_presigned_download_url(key=media.thumbnail_key, expires_in=3600)
        if media.thumbnail_key
        else None
    )
    return ImageFieldValue(url=photo_url, thumbnail_url=thumbnail_url)


# Union of all field value types
FieldValue = (
    StringFieldValue
    | IntFieldValue
    | FloatFieldValue
    | BoolFieldValue
    | EnumFieldValue
    | DateFieldValue
    | DatetimeFieldValue
    | USDFieldValue
    | EmailFieldValue
    | URLFieldValue
    | ObjectFieldValue
    | TextFieldValue
    | ImageFieldValue
)


class ObjectFieldDTO(BaseSchema):
    """DTO for object field representation."""

    key: str
    value: FieldValue | None
    label: str | None = None
    editable: bool = True


@dataclass(frozen=True)
class ObjectColumn:
    """Internal column configuration for object definitions.

    This is used to define columns in BaseObject.column_definitions.
    It includes internal metadata like accessor/formatter that are not exposed via API.
    """

    key: str  # Internal identifier (e.g., database column name)
    label: str
    type: FieldType
    value: Callable[[Any], FieldValue | None]  # Returns wrapped FieldValue type
    sortable: bool = True
    default_visible: bool = True
    available_values: list[str] | None = None
    object_type: ObjectTypes | None = None  # Type of referenced object (for Object field type)

    # Internal-only fields (not exposed via API)
    editable: bool = True  # Whether field can be edited
    nullable: bool = False  # Whether field value can be None
    include_in_list: bool = True  # Whether to include in list view DTOs


class ColumnDefinitionSchema(BaseSchema):
    """External API schema for column definitions.

    This is returned by the schema endpoint and contains only serializable fields.
    """

    key: str  # Column identifier (used for filtering/sorting)
    label: str
    type: FieldType
    filter_type: FilterType
    sortable: bool = True
    default_visible: bool = True
    available_values: list[str] | None = None
    object_type: ObjectTypes | None = None


class ObjectRelationGroup(BaseSchema):
    """A group of related objects with metadata.

    Groups related objects by relationship type (e.g., all media for a deliverable)
    and provides rich data by reusing ObjectListSchema.
    """

    relation_name: str  # e.g., "campaign", "media", "brand"
    relation_label: str  # Human-readable: "Campaign", "Media Files"
    relation_type: RelationType
    cardinality: RelationCardinality

    # Reuse ObjectListSchema - includes title, subtitle, state, fields, actions, link
    objects: list["ObjectListSchema"]


class ObjectListSchema(BaseSchema):
    """External API schema for object list representation."""

    id: str
    object_type: ObjectTypes
    title: str
    state: str | None
    created_at: datetime
    updated_at: datetime
    subtitle: str | None = None
    actions: list[ActionDTO] = []
    fields: list[ObjectFieldDTO] = []
    link: str | None = None

    def __post_init__(self) -> None:
        self.link = f"/{self.object_type}/{self.id}"


class ObjectListRequest(BaseSchema):
    """Request schema for listing objects."""

    limit: int = 50
    offset: int = 0
    filters: list[FilterDefinition] = []
    sorts: list[SortDefinition] = []
    search: str | None = None
    column: list[str] | None = None


class ObjectListResponse(BaseSchema):
    """Response schema for object lists."""

    objects: list[ObjectListSchema]
    total: int
    limit: int
    offset: int
    actions: list[ActionDTO] = []


class ObjectSchemaResponse(BaseSchema):
    """Schema metadata for an object type."""

    columns: list[ColumnDefinitionSchema]


# ============================================================================
# Time Series Schemas
# ============================================================================


class TimeSeriesDataRequest(BaseSchema):
    """Request schema for time series data queries."""

    field: str  # Column name to aggregate
    time_range: TimeRange | None = None  # Relative time range
    start_date: datetime | None = None  # Absolute start (overrides time_range)
    end_date: datetime | None = None  # Absolute end (overrides time_range)
    granularity: Granularity = Granularity.automatic  # Time bucket size
    aggregation: AggregationType | None = None  # Aggregation type (auto-determined if None)
    filters: list[FilterDefinition] = []  # Reuse existing filter system
    fill_missing: bool = True  # Deprecated: gaps are now always filled via SQL (kept for API compatibility)


class NumericalDataPoint(BaseSchema):
    """A single numerical data point."""

    timestamp: datetime
    value: float | int | None
    count: int  # Number of records in this bucket


class CategoricalDataPoint(BaseSchema):
    """A single categorical data point with breakdowns."""

    timestamp: datetime
    breakdowns: dict[str, int]  # category -> count mapping
    total_count: int


class NumericalTimeSeriesData(BaseSchema, tag="numerical"):
    """Numerical time series data response."""

    data_points: list[NumericalDataPoint]


class CategoricalTimeSeriesData(BaseSchema, tag="categorical"):
    """Categorical time series data response."""

    data_points: list[CategoricalDataPoint]


TimeSeriesData = NumericalTimeSeriesData | CategoricalTimeSeriesData


class TimeSeriesDataResponse(BaseSchema):
    """Response schema for time series data queries."""

    data: TimeSeriesData
    field_name: str
    field_type: FieldType
    aggregation_type: AggregationType
    granularity_used: Granularity
    start_date: datetime
    end_date: datetime
    total_records: int  # Total records considered (after filters)
