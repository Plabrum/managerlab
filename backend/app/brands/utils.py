"""Brand utility functions."""

from sqlalchemy import func, select
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
    Get existing brand by name (case-insensitive) or create new brand.

    Args:
        session: Database session
        name: Brand name to search for or create
        team_id: Team ID for scoping (RLS)
        email: Optional email to set when creating new brand

    Returns:
        Brand instance (either existing or newly created)
    """
    # Try to find existing brand (case-insensitive)
    stmt = select(Brand).where(
        Brand.team_id == team_id,
        func.lower(Brand.name) == name.lower(),
    )
    result = await session.execute(stmt)
    existing_brand = result.scalar_one_or_none()

    if existing_brand:
        return existing_brand

    # Create new brand
    new_brand = Brand(
        name=name,
        email=email,
        team_id=team_id,
    )
    session.add(new_brand)
    await session.flush()
    return new_brand
