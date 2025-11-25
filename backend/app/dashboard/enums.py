"""Dashboard enums."""

from enum import StrEnum


class DashboardActions(StrEnum):
    """Dashboard action keys."""

    edit = "edit"
    update = "update"
    delete = "delete"


class WidgetActions(StrEnum):
    """Widget action keys."""

    create = "create"
    update = "update"
    delete = "delete"
    reorder = "reorder"


class WidgetType(StrEnum):
    """Widget visualization types."""

    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    STAT_NUMBER = "stat_number"
