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


def build_team_scope_filter(entity, team_id: int) -> ColumnElement[bool]:
    """Build team scope filter or return literal(True) if entity has no team_id."""
    try:
        return entity.team_id == team_id
    except AttributeError:
        return literal(True)


def build_campaign_scope_filter(entity, campaign_id: int) -> ColumnElement[bool]:
    """Build campaign scope filter."""
    return entity.campaign_id == campaign_id


# ---------------------------------------------------------------------------
# SCOPE DISPATCHER
# ---------------------------------------------------------------------------


def _build_scope_filter(
    entity, team_id: int | None, campaign_id: int | None, scope_type: ScopeType
) -> ColumnElement[bool]:
    """Build scope filter based on scope type."""
    if scope_type == ScopeType.TEAM and team_id:
        return build_team_scope_filter(entity, team_id)
    elif scope_type == ScopeType.CAMPAIGN and campaign_id:
        return build_campaign_scope_filter(entity, campaign_id)
    else:
        return literal(False)


# ---------------------------------------------------------------------------
# EVENT LISTENER FACTORY
# ---------------------------------------------------------------------------


def soft_delete_filter(execute_state):
    """Filter soft-deleted records. Bypass with execution_options(include_deleted=True)."""
    if (
        not execute_state.is_select
        or execute_state.is_column_load
        or execute_state.is_relationship_load
        or execute_state.execution_options.get("include_deleted", False)
    ):
        return

    def _filter(cls):
        try:
            return cls.deleted_at.is_(None)
        except AttributeError:
            return true()

    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(BaseDBModel, _filter, include_aliases=True)
    )


def create_query_filter(team_id: int | None, campaign_id: int | None, scope_type: ScopeType | None):
    """Create RLS query filter with captured scope values.

    Uses default arguments to avoid SQLAlchemy's lambda wrapping of closure variables.
    """
    is_system_mode = config.IS_SYSTEM_MODE

    def apply_query_filters(execute_state):
        if not execute_state.is_select or execute_state.is_column_load or execute_state.is_relationship_load:
            return

        def build_criteria(
            cls, _sys=is_system_mode, _scope=scope_type, _team=team_id, _camp=campaign_id
        ) -> ColumnElement[bool]:
            if _sys:
                return true()
            elif _scope is not None:
                return _build_scope_filter(cls, _team, _camp, _scope)
            else:
                raise ValueError("Scope type required for query filtering")

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(BaseDBModel, build_criteria, include_aliases=True)
        )

    return apply_query_filters
