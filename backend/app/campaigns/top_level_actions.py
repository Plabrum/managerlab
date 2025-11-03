from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseAction, action_group_factory
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.campaigns.enums import CampaignActions
from app.campaigns.models import Campaign, CampaignContract
from app.campaigns.schemas import CampaignCreateSchema
from app.utils.db import create_model

top_level_campaign_actions = action_group_factory(
    ActionGroupType.TopLevelCampaignActions,
    model_type=Campaign,
)


@top_level_campaign_actions
class CreateCampaign(BaseAction):
    action_key = CampaignActions.create
    label = "Create Campaign"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: CampaignCreateSchema,
        transaction: AsyncSession,
        team_id: int,
        user: int,
    ) -> ActionExecutionResponse:
        # Extract contract_document_id before creating campaign
        contract_document_id = data.contract_document_id

        # brand_id is already decoded from SQID string to int by msgspec
        new_campaign = await create_model(
            session=transaction,
            team_id=team_id,
            campaign_id=None,
            model_class=Campaign,
            create_vals=data,
            user_id=user,
            ignore_fields=["contract_document_id"],
        )

        # If a contract document was provided, create the association
        if contract_document_id is not None:
            contract_association = CampaignContract(
                campaign_id=new_campaign.id,
                document_id=contract_document_id,
                team_id=team_id,
            )
            transaction.add(contract_association)

        return ActionExecutionResponse(
            message=f"Created campaign '{new_campaign.name}'",
        )
