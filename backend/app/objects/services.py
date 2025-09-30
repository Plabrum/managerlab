from typing import assert_never
from sqlalchemy import Select, and_

from app.base.models import BaseDBModel
from app.objects.enums import FieldType, FilterType
from app.objects.schemas import (
    BooleanFilterDefinition,
    DateFilterDefinition,
    FilterDefinition,
    RangeFilterDefinition,
    TextFilterDefinition,
)


def apply_filter(
    query: Select, model_class: type[BaseDBModel], filter_def: FilterDefinition
) -> Select:
    column = getattr(model_class, filter_def.column, None)
    if column is None:
        return query

    match filter_def:
        # ---------- Text ----------
        case TextFilterDefinition(operation="equals", value=v):
            return query.where(column == v)
        case TextFilterDefinition(operation="contains", value=v):
            return query.where(column.ilike(f"%{v}%"))
        case TextFilterDefinition(operation="starts_with", value=v):
            return query.where(column.ilike(f"{v}%"))
        case TextFilterDefinition(operation="ends_with", value=v):
            return query.where(column.ilike(f"%{v}"))

        # ---------- Numeric Range ----------
        case RangeFilterDefinition(start=s, finish=e):
            conds = []
            if s is not None:
                conds.append(column >= s)
            if e is not None:
                conds.append(column <= e)
            return query.where(and_(*conds)) if conds else query

        # ---------- Boolean ----------
        case BooleanFilterDefinition(value=b):
            return query.where(column.is_(b))

        # ---------- Date/Time ----------
        case DateFilterDefinition(start=s, finish=e):
            conds = []
            if s is not None:
                conds.append(column >= s)
            if e is not None:
                conds.append(column <= e)
            return query.where(and_(*conds)) if conds else query

        case _:
            raise ValueError(f"Unknown filter definition type: {type(filter_def)}")


def get_filter_by_field_type(field_type: FieldType) -> FilterType:
    """Get default available filters for a field type."""
    match field_type:
        case FieldType.String | FieldType.Email | FieldType.URL | FieldType.Text:
            return FilterType.text_filter
        case FieldType.Int | FieldType.Float | FieldType.USD:
            return FilterType.range_filter
        case FieldType.Date | FieldType.Datetime:
            return FilterType.date_filter
        case FieldType.Bool:
            return FilterType.boolean_filter
        case FieldType.Enum:
            return FilterType.enum_filter
        case _:
            assert_never(field_type)
