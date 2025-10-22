"""Database utility functions for common operations."""

from litestar import Request
from litestar.exceptions import NotFoundException
from msgspec import structs
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.enums import ScopeType
from app.base.models import BaseDBModel
from app.base.schemas import BaseSchema


async def get_or_404[T: BaseDBModel](
    session: AsyncSession,
    model_class: type[T],
    id: int,
    load_options: list | None = None,
) -> T:
    query = select(model_class).where(model_class.id == id)
    if load_options:
        query = query.options(*load_options)

    result = await session.execute(query)
    entity = result.unique().scalar_one_or_none()
    if not entity:
        raise NotFoundException(detail="Not found")
    return entity


def update_model[T](model_instance: T, update_vals: BaseSchema) -> T:
    """Update a model instance from a DTO/struct."""
    for field, value in structs.asdict(update_vals).items():
        if hasattr(model_instance, field):
            setattr(model_instance, field, value)
    return model_instance


def create_model[T](
    team_id: int | None,
    campaign_id: int | None,
    model_class: type[T],
    create_vals: BaseSchema,
) -> T:
    """Create a new model instance from a DTO/struct."""
    data = {
        field: value
        for field, value in structs.asdict(create_vals).items()
        if value is not None
    }
    rls_fields = {"team_id": team_id, "campaign_id": campaign_id}
    return model_class(**data, **rls_fields)


async def set_rls_variables(session: AsyncSession, request: Request) -> None:
    """Set PostgreSQL RLS session variables within an active transaction.

    Sets session variables for Row-Level Security based on session scope:
    - app.team_id: Set when user has team scope
    - app.campaign_id: Set when user has campaign scope
    - Neither set for admin/system operations

    Note: Must be called within an active transaction (after begin()).
    SET LOCAL is transaction-scoped and doesn't support parameter binding.
    """
    scope_type = request.session.get("scope_type")

    if scope_type == ScopeType.TEAM.value:
        team_id = request.session.get("team_id")
        if team_id:
            # Validate team_id is an integer to prevent SQL injection
            team_id_int = int(team_id)
            await session.execute(text(f"SET LOCAL app.team_id = {team_id_int}"))

    elif scope_type == ScopeType.CAMPAIGN.value:
        campaign_id = request.session.get("campaign_id")
        if campaign_id:
            # Validate campaign_id is an integer to prevent SQL injection
            campaign_id_int = int(campaign_id)
            await session.execute(
                text(f"SET LOCAL app.campaign_id = {campaign_id_int}")
            )
