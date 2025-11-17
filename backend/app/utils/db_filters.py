import structlog
from sqlalchemy import and_, literal, or_, true
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql.elements import ColumnElement

from app.auth.enums import ScopeType
from app.base.models import BaseDBModel
from app.utils.configure import config

logger = structlog.getLogger(__name__)

# ---------------------------------------------------------------------------
# CORE FILTER BUILDERS
# ---------------------------------------------------------------------------


def build_team_scope_filter(cls, team_id: int) -> ColumnElement[bool]:
    if not hasattr(cls, "team_id"):
        return literal(True)
    return cls.team_id == team_id


def build_campaign_scope_filter(cls, campaign_id: int) -> ColumnElement[bool]:
    if not hasattr(cls, "campaign_id"):
        raise ValueError(f"{cls.__name__} does not support campaign scoping")
    return cls.campaign_id == campaign_id


# ---------------------------------------------------------------------------
# SCOPE DISPATCHER
# ---------------------------------------------------------------------------


def _build_scope_filter(
    cls,
    team_id: int | None,
    campaign_id: int | None,
    scope_type: ScopeType | None,
) -> ColumnElement[bool] | None:
    """Return a scope filter for this class, or None if no scope_type."""

    # No scope → nothing to filter
    if scope_type is None:
        return None

    # TEAM SCOPE ------------------------------------------------------------
    if scope_type == ScopeType.TEAM and team_id:
        return build_team_scope_filter(cls, team_id)

    # CAMPAIGN SCOPE --------------------------------------------------------
    elif scope_type == ScopeType.CAMPAIGN and campaign_id:
        return build_campaign_scope_filter(cls, campaign_id)

    else:
        logger.warning(
            "Invalid scope configuration",
            cls.__name__,
            scope_type=scope_type,
            team_id=team_id,
            campaign_id=campaign_id,
        )
        return literal(False)


# ---------------------------------------------------------------------------
# EVENT LISTENER FACTORY
# ---------------------------------------------------------------------------


def create_query_filter(
    team_id: int | None,
    campaign_id: int | None,
    scope_type: ScopeType | None,
):
    """Factory that creates a query filter with captured scope values.

    Args:
        team_id: Team ID from request session (or None)
        campaign_id: Campaign ID from request session (or None)
        scope_type: Scope type ("team", "campaign", or None)

    Returns:
        Filter function for do_orm_execute event listener.
    """

    def apply_query_filters(execute_state):
        """Apply automatic filtering based on captured scope."""
        # Early returns for non-SELECT or column/relationship loads
        if not execute_state.is_select or execute_state.is_column_load or execute_state.is_relationship_load:
            return

        def build_criteria(cls) -> ColumnElement[bool]:
            filters: list[ColumnElement[bool]] = []

            # Always filter soft deletes
            if hasattr(cls, "deleted_at"):
                filters.append(cls.deleted_at.is_(None))

            # Add scope-specific filters (skip in system mode)
            if not config.IS_SYSTEM_MODE:
                scope_filter = _build_scope_filter(
                    cls=cls,
                    team_id=team_id,
                    campaign_id=campaign_id,
                    scope_type=scope_type,
                )
                if scope_filter is not None:
                    filters.append(scope_filter)

            # Combine all filters with AND, or return true() if no filters
            return and_(*filters) if filters else true()

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(BaseDBModel, build_criteria, include_aliases=True)
        )

    return apply_query_filters
