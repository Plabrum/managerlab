"""Database query filters for soft deletes.

This module provides SQLAlchemy event listeners for automatic filtering
of soft-deleted records. Scope filtering is handled by PostgreSQL RLS.
"""

from sqlalchemy.orm import raiseload


def apply_soft_delete_filter(execute_state):
    """SQLAlchemy event listener that filters soft-deleted records from SELECT queries.

    This function is called for every ORM execute event and:
    1. Filters out soft-deleted records (deleted_at IS NULL)
    2. Enforces eager loading with raiseload

    Note: Scope filtering (team_id/campaign_id) is handled by PostgreSQL
    Row-Level Security policies. See app/base/scope_mixins.py for RLS setup.

    Args:
        execute_state: SQLAlchemy execute state object
    """
    if not execute_state.is_select:
        return

    statement = execute_state.statement

    # Get the model from the statement
    from_clause = list(statement.get_final_froms())
    if not from_clause:
        return

    # Get the mapped class (model)
    mapper = from_clause[0]
    if not hasattr(mapper, "entity"):
        return

    model = mapper.entity

    # Apply soft delete filter (all models have deleted_at from BaseDBModel)
    if hasattr(model, "deleted_at"):
        statement = statement.where(model.deleted_at.is_(None))

    # Apply raiseload for eager loading enforcement
    statement = statement.options(raiseload("*"))

    execute_state.statement = statement
