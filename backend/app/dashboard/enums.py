"""Dashboard enums."""

from enum import StrEnum, auto


class DashboardActions(StrEnum):
    """Dashboard action keys."""

    create = "create"
    edit = "edit"
    update = "update"
    delete = "delete"


class WidgetActions(StrEnum):
    """Widget action keys."""

    create = auto()
    edit = auto()
    delete = auto()


class WidgetType(StrEnum):
    """Widget visualization types."""

    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    STAT_NUMBER = "stat_number"
