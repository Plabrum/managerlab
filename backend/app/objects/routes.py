from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from litestar import Router, get, post

from app.base.models import BaseDBModel
from app.objects.base import ObjectRegistry
from app.actions.registry import ActionRegistry
from app.objects.schemas import (
    ObjectListRequest,
    ObjectListResponse,
    ObjectSchemaResponse,
    TimeSeriesDataRequest,
    TimeSeriesDataResponse,
    NumericalDataPoint,
    NumericalTimeSeriesData,
    CategoricalTimeSeriesData,
)
from app.objects.services import (
    resolve_time_range,
    determine_granularity,
    get_default_aggregation,
    query_time_series_data,
)
from app.objects.enums import ObjectTypes
from app.utils.logging import logger
from app.utils.discovery import discover_and_import

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
    return ObjectSchemaResponse(columns=object_service.column_definitions)


@post("/{object_type:str}", operation_id="list_objects")
async def list_objects(
    object_type: ObjectTypes,
    data: ObjectListRequest,
    transaction: AsyncSession,
    object_registry: ObjectRegistry,
    action_registry: ActionRegistry,
) -> ObjectListResponse:
    logger.info(f"data:{data}")
    object_service = object_registry.get_class(object_type)
    objects: Sequence[BaseDBModel]
    objects, total = await object_service.get_list(transaction, data)
    columns = object_service.column_definitions

    # Get top-level actions for this object type (e.g., create)
    list_actions = []
    top_level_action_group_type = object_service.get_top_level_action_group()
    if top_level_action_group_type:
        top_level_action_group = action_registry.get_class(top_level_action_group_type)
        list_actions = top_level_action_group.get_available_actions()

    # Convert objects to DTOs (async)
    object_dtos = [object_service.to_list_dto(obj) for obj in objects]

    return ObjectListResponse(
        objects=object_dtos,
        total=total,
        limit=data.limit,
        offset=data.offset,
        columns=columns,
        actions=list_actions,
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
    start_date, end_date = resolve_time_range(
        data.time_range, data.start_date, data.end_date
    )

    # Determine granularity
    granularity = determine_granularity(data.granularity, start_date, end_date)

    # Determine aggregation type
    aggregation = data.aggregation or get_default_aggregation(field_type)

    # Query data
    data_points, total_records = await query_time_series_data(
        session=transaction,
        model_class=object_service.model,
        field_name=data.field,
        field_type=field_type,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        aggregation=aggregation,
        filters=data.filters,
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
