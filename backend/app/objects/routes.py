from collections.abc import Sequence

import structlog
from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.models import BaseDBModel
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    CategoricalTimeSeriesData,
    NumericalDataPoint,
    NumericalTimeSeriesData,
    ObjectListRequest,
    ObjectListResponse,
    ObjectSchemaResponse,
    TimeSeriesDataRequest,
    TimeSeriesDataResponse,
)
from app.objects.services import (
    determine_granularity,
    get_default_aggregation,
    query_time_series_data,
    resolve_time_range,
)
from app.utils.discovery import discover_and_import

logger = structlog.get_logger(__name__)

# Auto-discover all object files to trigger registration with ObjectRegistry
# This happens here (not in __init__.py) to avoid circular imports during module loading
discover_and_import(["objects.py", "objects/**/*.py"], base_path="app")


@get("/{object_type:str}/schema")
async def get_object_schema(
    object_type: ObjectTypes,
    object_registry: ObjectRegistry,
) -> ObjectSchemaResponse:
    """Get schema metadata for an object type (column definitions)."""
    object_service = object_registry.get_class(object_type)
    # Convert internal ObjectColumn to external ColumnDefinitionSchema
    return ObjectSchemaResponse(columns=object_service.get_column_schemas())


@post("/{object_type:str}", operation_id="list_objects")
async def list_objects(
    object_type: ObjectTypes,
    data: ObjectListRequest,
    transaction: AsyncSession,
    object_registry: ObjectRegistry,
) -> ObjectListResponse:
    logger.info(f"data:{data}")
    object_service = object_registry.get_class(object_type)
    objects: Sequence[BaseDBModel]
    objects, total = await object_service.get_list(transaction, data)

    # Convert objects to schemas
    object_schemas = [object_service.to_list_schema(obj) for obj in objects]

    return ObjectListResponse(
        objects=object_schemas,
        total=total,
        limit=data.limit,
        offset=data.offset,
        actions=object_service.get_top_level_actions(),
    )


@post("/{object_type:str}/data", operation_id="get_time_series_data")
async def get_time_series_data(
    object_type: ObjectTypes,
    data: TimeSeriesDataRequest,
    transaction: AsyncSession,
    object_registry: ObjectRegistry,
) -> TimeSeriesDataResponse:
    logger.info(f"Time series request for {object_type}: {data}")

    # Get object service
    object_service = object_registry.get_class(object_type)

    # Validate field exists and get metadata
    object_service.validate_field_exists(data.field)
    field_metadata = object_service.get_field_metadata(data.field)

    if field_metadata is None:
        raise ValueError(f"Field {data.field} not found")

    field_type = field_metadata.type

    # Resolve time range
    start_date, end_date = resolve_time_range(data.time_range, data.start_date, data.end_date)

    # Determine granularity
    granularity = determine_granularity(data.granularity, start_date, end_date)

    # Determine aggregation type
    aggregation = data.aggregation or get_default_aggregation(field_type)

    # Query data
    data_points, total_records = await query_time_series_data(
        session=transaction,
        model_class=object_service.model(),
        field_name=data.field,
        field_type=field_type,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        aggregation=aggregation,
        filters=data.filters,
        query_relationship=field_metadata.query_relationship,
        query_column=field_metadata.query_column,
    )

    # Wrap data in appropriate discriminated union type
    # Note: query_time_series_data now always returns complete data with gaps filled via SQL
    if isinstance(data_points, list) and len(data_points) > 0:
        if isinstance(data_points[0], NumericalDataPoint):
            time_series_data = NumericalTimeSeriesData(data_points=data_points)  # type: ignore
        else:
            # Categorical data
            time_series_data = CategoricalTimeSeriesData(data_points=data_points)  # type: ignore
    else:
        # Empty data, default to numerical
        time_series_data = NumericalTimeSeriesData(data_points=[])

    return TimeSeriesDataResponse(
        data=time_series_data,
        field_name=data.field,
        field_type=field_type,
        aggregation_type=aggregation,
        granularity_used=granularity,
        start_date=start_date,
        end_date=end_date,
        total_records=total_records,
    )


# Object router
object_router = Router(
    path="/o",
    route_handlers=[
        get_object_schema,
        list_objects,
        get_time_series_data,
    ],
    tags=["objects"],
)
