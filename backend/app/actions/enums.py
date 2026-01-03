from enum import StrEnum, auto


class ActionGroupType(StrEnum):
    """Types of action groups."""

    MediaActions = "media_actions"
    DocumentActions = "document_actions"
    DeliverableActions = "deliverable_actions"
    DeliverableMediaActions = "deliverable_media_actions"
    BrandActions = "brand_actions"
    CampaignActions = "campaign_actions"
    InvoiceActions = "invoice_actions"
    RosterActions = "roster_actions"
    DashboardActions = "dashboard_actions"
    WidgetActions = "widget_actions"
    TeamActions = "team_actions"
    MessageActions = "message_actions"
    SavedViewActions = "saved_view_actions"
    UserActions = "user_actions"


class ActionResultType(StrEnum):
    """Types of actions the frontend should take after action execution."""

    redirect = "redirect"
    download_file = "download_file"


class ActionIcon(StrEnum):
    default = auto()
    refresh = auto()
    download = auto()
    send = auto()
    edit = auto()
    trash = auto()
    add = auto()
    check = auto()
    x = auto()
