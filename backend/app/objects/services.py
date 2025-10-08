from typing import assert_never
from sqlalchemy import Select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.models import BaseDBModel
from app.objects.enums import FieldType, FilterType
from app.objects.schemas import (
    BooleanFilterDefinition,
    DateFilterDefinition,
    FilterDefinition,
    RangeFilterDefinition,
    TextFilterDefinition,
    ObjectListRequest,
    SortDefinition,
    EnumFilterDefinition,
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

        # ---------- Enum ----------
        case EnumFilterDefinition(values=vals):
            return query.where(column.in_(vals))

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


def apply_sorts(
    query: Select, model_class: type[BaseDBModel], sorts: list[SortDefinition]
) -> Select:
    """Apply sort definitions to a query."""
    for sort_def in sorts:
        column = getattr(model_class, sort_def.column, None)
        if column is None:
            continue

        if sort_def.direction.value == "asc":
            query = query.order_by(column.asc())
        else:
            query = query.order_by(column.desc())

    return query


async def export_to_csv(
    session: AsyncSession,
    model_class: type[BaseDBModel],
    request: ObjectListRequest,
    columns: list[str] | None = None,
) -> tuple[str, str]:
    """
    Export objects to CSV with filters and sorts applied.

    Args:
        session: Database session
        model_class: Model class to query
        request: ObjectListRequest with filters, sorts, search
        columns: Optional list of column keys to include (defaults to all visible columns)

    Returns:
        Tuple of (csv_content, filename)
    """
    import csv
    import io
    from sqlalchemy import select

    # Build base query
    stmt = select(model_class)

    # Apply filters
    for filter_def in request.filters:
        stmt = apply_filter(stmt, model_class, filter_def)

    # Apply sorts
    stmt = apply_sorts(stmt, model_class, request.sorts)

    # Execute query
    result = await session.execute(stmt)
    objects = list(result.scalars().all())

    if not objects:
        return "", f"{model_class.__name__.lower()}_export.csv"

    # Generate CSV
    output = io.StringIO()

    # Determine columns to export
    if columns:
        fieldnames = columns
    elif request.column:
        fieldnames = request.column
    elif hasattr(objects[0], "to_dict"):
        # Fallback to all attributes
        fieldnames = list(objects[0].to_dict().keys())
    else:
        # Last resort - use __dict__ keys
        fieldnames = [k for k in objects[0].__dict__.keys() if not k.startswith("_")]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for obj in objects:
        if hasattr(obj, "to_dict"):
            row_data = obj.to_dict()
        else:
            row_data = {k: getattr(obj, k, None) for k in fieldnames}

        # Only include requested columns
        row = {k: row_data.get(k) for k in fieldnames}
        writer.writerow(row)

    csv_content = output.getvalue()
    filename = f"{model_class.__name__.lower()}_export.csv"

    return csv_content, filename
