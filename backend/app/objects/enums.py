from enum import StrEnum, auto


class ObjectTypes(StrEnum):
    Users = auto()
    Roster = auto()
    Brands = auto()
    BrandContacts = auto()
    Campaigns = auto()
    Posts = auto()
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


class FilterType(StrEnum):
    """Available filter types for different field types."""

    text_filter = auto()
    range_filter = auto()
    date_filter = auto()
    boolean_filter = auto()
    enum_filter = auto()


class SortDirection(StrEnum):
    """Sort direction options."""

    sort_asc = auto()
    sort_desc = auto()
