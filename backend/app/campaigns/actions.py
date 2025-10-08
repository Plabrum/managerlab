from app.actions import action_group_factory, ActionGroupType
from app.campaigns.models import Campaign


campaign_actions = action_group_factory(
    ActionGroupType.CampaignActions, model_type=Campaign
)
