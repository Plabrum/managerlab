from enum import StrEnum, auto


class ObjectTypes(StrEnum):
    User = auto()
    Brand = auto()
    BrandContact = auto()
    Campaign = auto()
    Post = auto()
    Media = auto()
    Invoice = auto()


class FieldType(StrEnum):
    """Field types for object fields."""

    String = auto()
    Int = auto()
    Float = auto()
    Bool = auto()
    Date = auto()
    Datetime = auto()
    USD = auto()
    Email = auto()
    URL = auto()
    Text = auto()


class FilterType(StrEnum):
    """Available filter types for different field types."""

    text = auto()
    range = auto()
    date = auto()
    boolean = auto()


class SortDirection(StrEnum):
    """Sort direction options."""

    asc = auto()
    desc = auto()
