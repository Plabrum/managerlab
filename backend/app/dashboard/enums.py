"""Dashboard enums."""

from enum import StrEnum, auto


class DashboardActions(StrEnum):
    """Dashboard action keys."""

    edit = "edit"
    update = "update"
    delete = "delete"


class WidgetActions(StrEnum):
    """Widget action keys."""

    create = auto()
    edit = auto()
    delete = auto()
    reorder = auto()


class WidgetType(StrEnum):
    """Widget visualization types."""

    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    STAT_NUMBER = "stat_number"


# Widget size constraints (grid columns x rows)
WIDGET_SIZE_CONSTRAINTS = {
    WidgetType.STAT_NUMBER: {"min_w": 1, "min_h": 1, "default_w": 1, "default_h": 1},
    WidgetType.BAR_CHART: {"min_w": 2, "min_h": 2, "default_w": 3, "default_h": 2},
    WidgetType.LINE_CHART: {"min_w": 2, "min_h": 2, "default_w": 3, "default_h": 2},
    WidgetType.PIE_CHART: {"min_w": 2, "min_h": 2, "default_w": 2, "default_h": 2},
}


def get_widget_size_constraints(widget_type: str) -> dict:
    """Get size constraints for a widget type."""
    # Convert string to WidgetType for lookup
    try:
        widget_type_enum = WidgetType(widget_type)
        return WIDGET_SIZE_CONSTRAINTS.get(
            widget_type_enum,
            {"min_w": 1, "min_h": 1, "default_w": 1, "default_h": 1},
        )
    except ValueError:
        return {"min_w": 1, "min_h": 1, "default_w": 1, "default_h": 1}
