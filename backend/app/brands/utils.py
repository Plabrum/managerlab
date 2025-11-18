"""Brand utility functions."""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.brands.models.brands import Brand


async def get_or_create_brand(
    session: AsyncSession,
    *,
    name: str,
    team_id: int,
    email: str | None = None,
) -> Brand:
    """
    Get existing brand by name or create new brand.

    Uses PostgreSQL INSERT ... ON CONFLICT to handle race conditions atomically.
    If a brand with the same team_id and name exists, returns the existing record
    instead of raising IntegrityError.

    Args:
        session: Database session
        name: Brand name to search for or create
        team_id: Team ID for scoping (RLS)
        email: Optional email to set when creating new brand

    Returns:
        Brand instance (either existing or newly created)
    """
    # Use INSERT ... ON CONFLICT DO NOTHING to handle race conditions
    # This is atomic and prevents IntegrityError when two tasks try to create
    # the same brand simultaneously
    stmt = (
        insert(Brand)
        .values(
            name=name,
            email=email,
            team_id=team_id,
        )
        .on_conflict_do_nothing(
            # Conflict target: unique index on (team_id, name)
            index_elements=["team_id", "name"]
        )
        .returning(Brand)
    )

    result = await session.execute(stmt)
    brand = result.scalar_one_or_none()

    if brand is not None:
        # Insert succeeded - return newly created brand
        await session.flush()
        return brand

    # Insert was skipped due to conflict - fetch existing brand
    stmt = select(Brand).where(
        Brand.team_id == team_id,
        Brand.name == name,
    )
    result = await session.execute(stmt)
    existing_brand = result.scalar_one()

    return existing_brand
