"""Database utility functions for common operations."""

from litestar import Request
from litestar.exceptions import NotFoundException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.enums import ScopeType


async def get_or_404[T](session: AsyncSession, model_class: type[T], id: int) -> T:
    """Get an entity by ID or raise a 404 exception."""
    entity = await session.get(model_class, id)
    if not entity:
        raise NotFoundException(detail="Not found")
    return entity


def update_model[T](model_instance: T, update_vals) -> T:
    """Update a model instance from a DTO/struct."""
    for field, value in update_vals.__dict__.items():
        if hasattr(model_instance, field):
            setattr(model_instance, field, value)
    return model_instance


def create_model[T](model_class: type[T], create_vals) -> T:
    """Create a new model instance from a DTO/struct."""
    data = {
        field: value
        for field, value in create_vals.__dict__.items()
        if value is not None
    }
    return model_class(**data)


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
