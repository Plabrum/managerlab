from enum import StrEnum, auto


class ActionGroupType(StrEnum):
    """Types of action groups."""

    MediaActions = "media_actions"
    TopLevelMediaActions = "top_level_media_actions"
    DeliverableActions = "deliverable_actions"
    DeliverableMediaActions = "deliverable_media_actions"
    TopLevelDeliverableActions = "top_level_deliverable_actions"
    BrandActions = "brand_actions"
    TopLevelBrandActions = "top_level_brand_actions"
    CampaignActions = "campaign_actions"
    TopLevelCampaignActions = "top_level_campaign_actions"
    InvoiceActions = "invoice_actions"
    TopLevelInvoiceActions = "top_level_invoice_actions"
    RosterActions = "roster_actions"
    TopLevelRosterActions = "top_level_roster_actions"
    DashboardActions = "dashboard_actions"
    TeamActions = "team_actions"
    MessageActions = "message_actions"


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
