"""Dashboard enums."""

from enum import StrEnum


class DashboardOwnerType(StrEnum):
    """Dashboard ownership types."""

    USER = "user"
    TEAM = "team"


class DashboardActions(StrEnum):
    """Dashboard action keys."""

    update = "update"
    delete = "delete"


class WidgetType(StrEnum):
    """Widget visualization types."""

    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    STAT_NUMBER = "stat_number"
