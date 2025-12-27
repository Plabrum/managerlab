"""SavedView schemas for request/response handling."""

from datetime import datetime
from typing import Any

from app.base.schemas import BaseSchema
from app.objects.enums import ObjectTypes
from app.utils.sqids import Sqid

# =============================================================================
# Config Schema (TanStack Table State + Display Mode)
# =============================================================================


class SavedViewConfigSchema(BaseSchema):
    """Configuration stored in SavedView.config JSONB field.

    This schema matches the TanStack Table state structure plus display mode.
    """

    # Required fields first
    display_mode: str  # 'table' | 'gallery' | 'card'

    # Optional fields with defaults
    schema_version: int = 1
    column_filters: list[dict[str, Any]] = []  # ColumnFiltersState
    column_visibility: dict[str, bool] = {}  # VisibilityState
    sorting: list[dict[str, Any]] = []  # SortingState [{ id, desc }]
    search_term: str | None = None
    page_size: int = 40


# =============================================================================
# SavedView Schemas
# =============================================================================


class SavedViewSchema(BaseSchema):
    """Response schema for SavedView (full details)."""

    id: Sqid | None  # None for hard-coded defaults
    name: str
    object_type: ObjectTypes
    config: SavedViewConfigSchema
    schema_version: int
    user_id: int | None  # NULL = team-shared, set = personal
    team_id: int | None  # None for hard-coded defaults
    is_personal: bool  # Convenience property
    is_default: bool
    created_at: datetime
    updated_at: datetime


class CreateSavedViewSchema(BaseSchema):
    """Schema for creating a new saved view.

    - To create a personal view: set is_personal=True (user_id will be set automatically)
    - To create a team-shared view: set is_personal=False
    - Only personal views can be marked as default
    """

    name: str
    object_type: ObjectTypes
    config: SavedViewConfigSchema
    is_personal: bool = True  # Default to personal views
    is_default: bool = False  # Mark as user's default for this object_type


class UpdateSavedViewSchema(BaseSchema):
    """Schema for updating a saved view (partial updates).

    Only name, config, and is_default can be updated.
    Object type and ownership cannot change.
    Setting is_default=True will clear other user defaults for that object_type.
    """

    name: str | None = None
    config: SavedViewConfigSchema | None = None
    is_default: bool | None = None
