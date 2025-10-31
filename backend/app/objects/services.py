from datetime import UTC, datetime, timedelta
from typing import assert_never

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.models import BaseDBModel
from app.objects.enums import (
    AggregationType,
    FieldType,
    FilterType,
    Granularity,
    TimeRange,
)
from app.objects.schemas import (
    BooleanFilterDefinition,
    CategoricalDataPoint,
    DateFilterDefinition,
    EnumFilterDefinition,
    FilterDefinition,
    NumericalDataPoint,
    ObjectListRequest,
    RangeFilterDefinition,
    SortDefinition,
    TextFilterDefinition,
)


def apply_filter(query: Select, model_class: type[BaseDBModel], filter_def: FilterDefinition) -> Select:
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
        case FieldType.Image:
            return FilterType.null_filter
        case _:
            assert_never(field_type)


def apply_sorts(query: Select, model_class: type[BaseDBModel], sorts: list[SortDefinition]) -> Select:
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


# ============================================================================
# Time Series Functions
# ============================================================================


def resolve_time_range(
    time_range: TimeRange | None, start_date: datetime | None, end_date: datetime | None
) -> tuple[datetime, datetime]:
    """Resolve time range to absolute start and end datetimes.

    Args:
        time_range: Relative time range enum
        start_date: Explicit start date (overrides time_range)
        end_date: Explicit end date (overrides time_range)

    Returns:
        Tuple of (start_datetime, end_datetime) in UTC
    """
    now = datetime.now(tz=UTC)

    # Explicit dates override time_range
    if start_date and end_date:
        return start_date, end_date

    # If only one explicit date is provided, use it with time_range
    if start_date and not end_date:
        end_date = now

    if end_date and not start_date:
        # Use time_range to calculate start, or default to 30 days
        if time_range:
            start_date = _calculate_start_from_range(time_range, end_date)
        else:
            start_date = end_date - timedelta(days=30)

    # Both are None, use time_range or default
    if not start_date and not end_date:
        end_date = now
        if time_range:
            start_date = _calculate_start_from_range(time_range, end_date)
        else:
            start_date = end_date - timedelta(days=30)  # default to last 30 days

    return start_date, end_date


def _calculate_start_from_range(time_range: TimeRange, end_date: datetime) -> datetime:
    """Calculate start date from relative time range."""
    match time_range:
        case TimeRange.last_7_days:
            return end_date - timedelta(days=7)
        case TimeRange.last_30_days:
            return end_date - timedelta(days=30)
        case TimeRange.last_90_days:
            return end_date - timedelta(days=90)
        case TimeRange.last_6_months:
            return end_date - timedelta(days=180)
        case TimeRange.last_year:
            return end_date - timedelta(days=365)
        case TimeRange.year_to_date:
            return end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        case TimeRange.month_to_date:
            return end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        case TimeRange.all_time:
            # Return a very old date (e.g., 10 years ago)
            return end_date - timedelta(days=3650)
        case _:
            assert_never(time_range)


def determine_granularity(granularity: Granularity, start_date: datetime, end_date: datetime) -> Granularity:
    """Determine appropriate granularity based on time range.

    Args:
        granularity: Requested granularity (may be 'auto')
        start_date: Start of time range
        end_date: End of time range

    Returns:
        Resolved granularity
    """
    if granularity != Granularity.automatic:
        return granularity

    # Auto-determine based on range
    delta = end_date - start_date

    if delta <= timedelta(days=1):
        return Granularity.hour
    elif delta <= timedelta(days=7):
        return Granularity.day
    elif delta <= timedelta(days=90):
        return Granularity.week
    elif delta <= timedelta(days=365):
        return Granularity.month
    elif delta <= timedelta(days=730):  # 2 years
        return Granularity.quarter
    else:
        return Granularity.year


def get_date_trunc_format(granularity: Granularity) -> str:
    """Get PostgreSQL date_trunc format string for granularity."""
    match granularity:
        case Granularity.hour:
            return "hour"
        case Granularity.day:
            return "day"
        case Granularity.week:
            return "week"
        case Granularity.month:
            return "month"
        case Granularity.quarter:
            return "quarter"
        case Granularity.year:
            return "year"
        case Granularity.automatic:
            raise ValueError("Granularity must be resolved before getting date_trunc format")
        case _:
            assert_never(granularity)


def get_default_aggregation(field_type: FieldType) -> AggregationType:
    """Get default aggregation type for a field type."""
    match field_type:
        case FieldType.Int | FieldType.Float | FieldType.USD:
            return AggregationType.sum
        case FieldType.String | FieldType.Enum | FieldType.Bool | FieldType.Email | FieldType.URL | FieldType.Text:
            return AggregationType.count_
        case FieldType.Date | FieldType.Datetime:
            return AggregationType.count_
        case FieldType.Image:
            return AggregationType.count_
        case _:
            assert_never(field_type)


def is_numerical_field(field_type: FieldType) -> bool:
    """Check if a field type is numerical."""
    return field_type in (FieldType.Int, FieldType.Float, FieldType.USD)


def is_categorical_field(field_type: FieldType) -> bool:
    """Check if a field type is categorical."""
    return field_type in (FieldType.String, FieldType.Enum, FieldType.Bool)


def get_series_interval(granularity: Granularity) -> str:
    """Get PostgreSQL interval string for generate_series."""
    match granularity:
        case Granularity.hour:
            return "1 hour"
        case Granularity.day:
            return "1 day"
        case Granularity.week:
            return "1 week"
        case Granularity.month:
            return "1 month"
        case Granularity.quarter:
            return "3 months"
        case Granularity.year:
            return "1 year"
        case Granularity.automatic:
            raise ValueError("Granularity must be resolved before getting series interval")
        case _:
            assert_never(granularity)


async def query_time_series_data(
    session: AsyncSession,
    model_class: type[BaseDBModel],
    field_name: str,
    field_type: FieldType,
    start_date: datetime,
    end_date: datetime,
    granularity: Granularity,
    aggregation: AggregationType,
    filters: list[FilterDefinition],
) -> tuple[list[NumericalDataPoint] | list[CategoricalDataPoint], int]:
    from sqlalchemy import text

    # Get the column reference
    column = getattr(model_class, field_name, None)
    if column is None:
        raise ValueError(f"Column {field_name} not found on {model_class.__name__}")

    # Get timestamp column (default to created_at)
    timestamp_column = model_class.created_at

    # Get date_trunc format and series interval
    trunc_format = get_date_trunc_format(granularity)
    series_interval = get_series_interval(granularity)

    # Build base query
    query = select(model_class)

    # Apply filters
    for filter_def in filters:
        query = apply_filter(query, model_class, filter_def)

    # Add time range filter
    query = query.where(timestamp_column >= start_date, timestamp_column <= end_date)

    # Count total records
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total_count = total_result.scalar_one()

    # Generate time series using generate_series
    # Use date_trunc on start_date to align to granularity boundary
    time_series = select(
        func.generate_series(
            func.date_trunc(trunc_format, start_date),
            func.date_trunc(trunc_format, end_date),
            text(f"interval '{series_interval}'"),
        ).label("time_bucket")
    ).subquery()

    # Handle categorical vs numerical aggregation
    if is_categorical_field(field_type) or aggregation == AggregationType.mode:
        # For categorical: GROUP BY time_bucket and field value, then count
        # Build aggregation directly from the filtered table
        time_bucket_expr = func.date_trunc(trunc_format, timestamp_column)

        agg_query = (
            select(
                time_bucket_expr.label("time_bucket"),
                column.label("category_value"),
                func.count().label("count"),
            )
            .where(timestamp_column >= start_date, timestamp_column <= end_date)
            .group_by(time_bucket_expr, column)
        )

        # Apply filters to aggregation query
        for filter_def in filters:
            agg_query = apply_filter(agg_query, model_class, filter_def)

        agg_subquery = agg_query.subquery()

        # Join with time series to fill gaps
        final_query = (
            select(
                time_series.c.time_bucket,
                agg_subquery.c.category_value,
                func.coalesce(agg_subquery.c.count, 0).label("count"),
            )
            .select_from(time_series)
            .outerjoin(
                agg_subquery,
                time_series.c.time_bucket == agg_subquery.c.time_bucket,
            )
            .order_by(time_series.c.time_bucket)
        )

        result = await session.execute(final_query)
        rows = result.all()

        # Convert to CategoricalBreakdown format
        # Note: generate_series ensures all time buckets exist
        breakdown_dict: dict[datetime, dict[str, int]] = {}
        for row in rows:
            bucket_time = row.time_bucket

            # Initialize bucket if needed
            if bucket_time not in breakdown_dict:
                breakdown_dict[bucket_time] = {}

            # Only add category if it has data (skip NULL categories from LEFT JOIN)
            if row.category_value is not None:
                category = str(row.category_value)
                breakdown_dict[bucket_time][category] = row.count

        categorical_data = [
            CategoricalDataPoint(
                timestamp=bucket,
                breakdowns=breakdowns,
                total_count=sum(breakdowns.values()),
            )
            for bucket, breakdowns in sorted(breakdown_dict.items())
        ]

        return categorical_data, total_count

    else:
        # For numerical: apply aggregation function
        match aggregation:
            case AggregationType.sum:
                agg_func = func.sum(column)
            case AggregationType.avg:
                agg_func = func.avg(column)
            case AggregationType.max:
                agg_func = func.max(column)
            case AggregationType.min:
                agg_func = func.min(column)
            case AggregationType.count:
                agg_func = func.count(column)
            case _:
                agg_func = func.sum(column)  # default fallback

        # Build aggregation directly from the filtered table
        time_bucket_expr = func.date_trunc(trunc_format, timestamp_column)

        agg_query = (
            select(
                time_bucket_expr.label("time_bucket"),
                agg_func.label("agg_value"),
                func.count().label("record_count"),
            )
            .where(timestamp_column >= start_date, timestamp_column <= end_date)
            .group_by(time_bucket_expr)
        )

        # Apply filters to aggregation query
        for filter_def in filters:
            agg_query = apply_filter(agg_query, model_class, filter_def)

        agg_subquery = agg_query.subquery()

        # Determine the default value for COALESCE based on field type
        # For datetime/date fields, use NULL; for numeric fields, use 0
        if field_type in (FieldType.Date, FieldType.Datetime):
            # For timestamp aggregations, we can't use 0, so use NULL
            default_agg_value = None
        else:
            # For numeric fields, use 0
            default_agg_value = 0

        # Join with time series to fill gaps using COALESCE
        # Only COALESCE the agg_value if it's numeric, otherwise leave as NULL
        if default_agg_value is not None:
            agg_value_expr = func.coalesce(agg_subquery.c.agg_value, default_agg_value).label("agg_value")
        else:
            agg_value_expr = agg_subquery.c.agg_value.label("agg_value")

        final_query = (
            select(
                time_series.c.time_bucket,
                agg_value_expr,
                func.coalesce(agg_subquery.c.record_count, 0).label("record_count"),
            )
            .select_from(time_series)
            .outerjoin(
                agg_subquery,
                time_series.c.time_bucket == agg_subquery.c.time_bucket,
            )
            .order_by(time_series.c.time_bucket)
        )

        result = await session.execute(final_query)
        rows = result.all()

        data_points = [
            NumericalDataPoint(
                timestamp=row.time_bucket,
                value=float(row.agg_value) if row.agg_value is not None else None,
                count=row.record_count,
            )
            for row in rows
        ]

        return data_points, total_count
