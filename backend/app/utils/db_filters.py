"""Database query filters using SQLAlchemy loader criteria.

Defense-in-depth architecture:
- Layer 1: PostgreSQL RLS (database-level)
- Layer 2: Application filters (ORM-level via event listeners)
"""

from sqlalchemy import and_, true
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql.elements import ColumnElement

from app.base.models import BaseDBModel
from app.utils.configure import config


def _build_scope_filter(
    cls, team_id: int | None, campaign_id: int | None, scope_type: str | None
) -> ColumnElement[bool] | None:
    """Build scope filter for team or campaign access."""
    # Team scope: filter by team_id
    if scope_type == "team" and team_id and hasattr(cls, "team_id"):
        return cls.team_id == team_id

    # Campaign scope: filter by campaign_id or team_id
    if scope_type == "campaign" and campaign_id:
        # Dual-scoped tables: allow access via team OR campaign
        if hasattr(cls, "campaign_id") and hasattr(cls, "team_id") and team_id:
            return (cls.team_id == team_id) | (cls.campaign_id == campaign_id)

        # Campaign-only tables
        if hasattr(cls, "campaign_id"):
            return cls.campaign_id == campaign_id

        # Team-scoped tables in campaign mode
        if hasattr(cls, "team_id") and team_id:
            return cls.team_id == team_id

    return None


def create_query_filter(team_id: int | None, campaign_id: int | None, scope_type: str | None):
    """Factory that creates a query filter with captured scope values.

    Args:
        team_id: Team ID from request session
        campaign_id: Campaign ID from request session
        scope_type: Scope type ("team" or "campaign")

    Returns:
        Filter function for do_orm_execute event listener
    """

    def apply_query_filters(execute_state):
        """Apply automatic filtering based on captured scope."""
        # Early returns for non-SELECT or relationship loads
        if not execute_state.is_select or execute_state.is_column_load or execute_state.is_relationship_load:
            return

        def build_criteria(cls) -> ColumnElement[bool]:
            filters: list[ColumnElement[bool]] = []

            # Always filter soft deletes
            if hasattr(cls, "deleted_at"):
                filters.append(cls.deleted_at.is_(None))

            # Add scope-specific filters (skip in system mode)
            if not config.IS_SYSTEM_MODE:
                scope_filter = _build_scope_filter(cls, team_id, campaign_id, scope_type)
                if scope_filter is not None:
                    filters.append(scope_filter)

            # Combine all filters with AND, or return true() if no filters
            return and_(*filters) if filters else true()

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(BaseDBModel, build_criteria, include_aliases=True)
        )

    return apply_query_filters
