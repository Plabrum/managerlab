"""Hard-coded default view configurations.

These defaults are returned when a user hasn't set a default view for an object type.
Each object type has an opinionated default configuration tailored to its common use case.
"""

from app.objects.enums import ObjectTypes
from app.views.schemas import SavedViewConfigSchema

# Opinionated defaults per object type
DEFAULT_VIEW_CONFIGS: dict[ObjectTypes, SavedViewConfigSchema] = {
    ObjectTypes.Roster: SavedViewConfigSchema(
        display_mode="card",
        column_filters=[],
        column_visibility={"email": True, "role": True, "status": True},
        sorting=[{"id": "name", "desc": False}],  # Alphabetical by name
        page_size=50,  # Show more roster members per page
    ),
    ObjectTypes.Campaigns: SavedViewConfigSchema(
        display_mode="table",
        column_filters=[],
        column_visibility={},
        sorting=[{"id": "created_at", "desc": True}],  # Newest first
        page_size=20,  # Fewer items in gallery mode
    ),
    ObjectTypes.Brands: SavedViewConfigSchema(
        display_mode="table",
        column_filters=[],
        column_visibility={"name": True, "website": True},
        sorting=[{"id": "name", "desc": False}],  # Alphabetical
        page_size=30,
    ),
    ObjectTypes.Deliverables: SavedViewConfigSchema(
        display_mode="card",
        column_filters=[],
        column_visibility={"title": True, "status": True, "due_date": True},
        sorting=[{"id": "due_date", "desc": False}],  # Soonest due date first
        page_size=40,
    ),
    ObjectTypes.Media: SavedViewConfigSchema(
        display_mode="gallery",
        column_filters=[],
        column_visibility={},
        sorting=[{"id": "created_at", "desc": True}],
        page_size=24,  # Grid layout friendly
    ),
    ObjectTypes.Documents: SavedViewConfigSchema(
        display_mode="gallery",
        column_filters=[],
        column_visibility={"name": True, "created_at": True, "size": True},
        sorting=[{"id": "created_at", "desc": True}],
        page_size=40,
    ),
    ObjectTypes.Invoices: SavedViewConfigSchema(
        display_mode="table",
        column_filters=[],
        column_visibility={
            "number": True,
            "status": True,
            "amount": True,
            "due_date": True,
        },
        sorting=[{"id": "created_at", "desc": True}],
        page_size=40,
    ),
}


def get_default_view_config(object_type: ObjectTypes) -> SavedViewConfigSchema:
    """Get the hard-coded default configuration for an object type.

    Args:
        object_type: The type of object to get default config for

    Returns:
        SavedViewConfigSchema with opinionated defaults for that object type,
        or generic table view if object type not found in DEFAULT_VIEW_CONFIGS

    Example:
        >>> config = get_default_view_config(ObjectTypes.Campaigns)
        >>> config.display_mode
        'gallery'
    """
    return DEFAULT_VIEW_CONFIGS.get(
        object_type,
        # Generic fallback for object types without custom defaults
        SavedViewConfigSchema(
            display_mode="table",
            column_filters=[],
            column_visibility={},
            sorting=[],
            page_size=40,
        ),
    )
