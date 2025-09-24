"""Object query utilities."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from litestar.exceptions import NotFoundException, ClientException

from app.objects.models.base import BaseObject
from app.objects.schemas import ObjectListRequest
from app.objects.services.base import get_object_model_class


async def get_object_by_sqid(
    session: AsyncSession, object_type: str, sqid: str
) -> BaseObject:
    """Get an object by its SQID."""
    model_class = get_object_model_class(object_type)

    try:
        object_id = BaseObject.decode_sqid(sqid)
    except ValueError:
        raise ClientException(f"Invalid SQID: {sqid}")

    stmt = select(model_class).where(model_class.id == object_id)
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()

    if not obj:
        raise NotFoundException(f"{object_type.title()} with SQID {sqid} not found")

    return obj


async def query_objects(
    session: AsyncSession, object_type: str, request: ObjectListRequest
) -> tuple[list[BaseObject], int]:
    """Query objects with filtering, sorting, and pagination."""
    model_class = get_object_model_class(object_type)

    # Build base query
    stmt = select(model_class).where(model_class.object_type == object_type)

    # Apply filters
    if request.filters:
        for key, value in request.filters.items():
            if hasattr(model_class, key):
                column = getattr(model_class, key)
                if isinstance(value, list):
                    stmt = stmt.where(column.in_(value))
                else:
                    stmt = stmt.where(column == value)

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar()

    # Apply sorting
    if request.sort_by and hasattr(model_class, request.sort_by):
        sort_column = getattr(model_class, request.sort_by)
        if request.sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())
    else:
        # Default sort by created_at desc
        stmt = stmt.order_by(model_class.created_at.desc())

    # Apply pagination
    stmt = stmt.limit(request.limit).offset(request.offset)

    # Execute query
    result = await session.execute(stmt)
    objects = list(result.scalars().all())

    return objects, total
