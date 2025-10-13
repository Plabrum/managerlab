from enum import StrEnum, auto


class ActionGroupType(StrEnum):
    """Types of action groups."""

    MediaActions = "media_actions"
    TopLevelMediaActions = "top_level_media_actions"
    PostActions = "post_actions"
    TopLevelPostActions = "top_level_post_actions"
    BrandActions = "brand_actions"
    CampaignActions = "campaign_actions"
    TopLevelCampaignActions = "top_level_campaign_actions"
    InvoiceActions = "invoice_actions"
    TopLevelInvoiceActions = "top_level_invoice_actions"


class ActionIcon(StrEnum):
    default = auto()
    refresh = auto()
    download = auto()
    send = auto()
    edit = auto()
    trash = auto()
    add = auto()
