from enum import StrEnum, auto


class ObjectTypes(StrEnum):
    Users = auto()
    Roster = auto()
    Brands = auto()
    BrandContacts = auto()
    Campaigns = auto()
    Deliverables = auto()
    Media = auto()
    Invoices = auto()


class FieldType(StrEnum):
    """Field types for object fields."""

    String = auto()
    Int = auto()
    Float = auto()
    Enum = auto()
    Bool = auto()
    Date = auto()
    Datetime = auto()
    USD = auto()
    Email = auto()
    URL = auto()
    Text = auto()
    Image = auto()


class FilterType(StrEnum):
    """Available filter types for different field types."""

    text_filter = auto()
    range_filter = auto()
    date_filter = auto()
    boolean_filter = auto()
    enum_filter = auto()
    null_filter = auto()


class SortDirection(StrEnum):
    """Sort direction options."""

    sort_asc = auto()
    sort_desc = auto()


class TimeRange(StrEnum):
    """Relative time range options for time series queries."""

    last_7_days = auto()
    last_30_days = auto()
    last_90_days = auto()
    last_6_months = auto()
    last_year = auto()
    year_to_date = auto()
    month_to_date = auto()
    all_time = auto()


class Granularity(StrEnum):
    """Time series granularity/bucketing options."""

    automatic = auto()
    hour = auto()
    day = auto()
    week = auto()
    month = auto()
    quarter = auto()
    year = auto()


class AggregationType(StrEnum):
    """Aggregation types for time series data."""

    # Numerical aggregations
    sum = auto()
    avg = auto()
    max = auto()
    min = auto()
    count = auto()

    # Categorical aggregations
    mode = auto()  # most frequent value
