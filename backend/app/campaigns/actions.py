from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseAction, action_group_factory
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.campaigns.enums import CampaignActions
from app.campaigns.models import Campaign, CampaignContract
from app.campaigns.schemas import (
    AddContractToCampaignSchema,
    AddDeliverableToCampaignSchema,
    CampaignUpdateSchema,
    ReplaceContractSchema,
)
from app.deliverables.models import Deliverable
from app.utils.db import create_model, update_model

campaign_actions = action_group_factory(
    ActionGroupType.CampaignActions,
    model_type=Campaign,
)


@campaign_actions
class DeleteCampaign(BaseAction):
    action_key = CampaignActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this campaign?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls,
        obj: Campaign,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted campaign",
        )


@campaign_actions
class UpdateCampaign(BaseAction):
    action_key = CampaignActions.update
    label = "Update"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Campaign,
        data: CampaignUpdateSchema,
        transaction: AsyncSession,
        user: int,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated campaign",
        )


@campaign_actions
class AddDeliverableToCampaign(BaseAction):
    """Add a new deliverable to a campaign."""

    action_key = CampaignActions.add_deliverable
    label = "Add Deliverable"
    is_bulk_allowed = False
    priority = 10
    icon = ActionIcon.add
    model = Campaign

    @classmethod
    async def execute(
        cls,
        obj: Campaign,
        data: AddDeliverableToCampaignSchema,
        transaction: AsyncSession,
        team_id: int,
        user: int,
    ) -> ActionExecutionResponse:
        # Create a new deliverable associated with this campaign
        await create_model(
            session=transaction,
            team_id=team_id,
            campaign_id=obj.id,
            model_class=Deliverable,
            create_vals=data,
            user_id=user,
        )

        return ActionExecutionResponse(
            message=f"Added deliverable '{data.title}' to campaign",
            invalidate_queries=["/o/deliverables"],
        )


@campaign_actions
class AddContractToCampaign(BaseAction):
    """Add initial contract to a campaign."""

    action_key = CampaignActions.add_contract
    label = "Add Contract"
    is_bulk_allowed = False
    priority = 15
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        obj: Campaign,
        data: AddContractToCampaignSchema,
        transaction: AsyncSession,
        team_id: int,
    ) -> ActionExecutionResponse:
        # Create association
        association = CampaignContract(
            campaign_id=obj.id,
            document_id=data.document_id,
            team_id=team_id,
        )
        transaction.add(association)

        return ActionExecutionResponse(
            message=f"Contract added to campaign '{obj.name}'",
        )

    @classmethod
    def is_available(cls, obj: Campaign | None) -> bool:
        # Only available if campaign has no contract
        return obj is not None and obj.contract is None


@campaign_actions
class ReplaceContract(BaseAction):
    """Replace existing contract with new version."""

    action_key = CampaignActions.replace_contract
    label = "Replace Contract"
    is_bulk_allowed = False
    priority = 16
    icon = ActionIcon.refresh

    @classmethod
    async def execute(
        cls,
        obj: Campaign,
        data: ReplaceContractSchema,
        transaction: AsyncSession,
        team_id: int,
    ) -> ActionExecutionResponse:
        # Create new association (becomes latest via created_at)
        association = CampaignContract(
            campaign_id=obj.id,
            document_id=data.document_id,
            team_id=team_id,
        )
        transaction.add(association)

        return ActionExecutionResponse(
            message=f"Contract replaced for campaign '{obj.name}'",
        )

    @classmethod
    def is_available(cls, obj: Campaign | None) -> bool:
        # Only available if campaign already has a contract
        return obj is not None and obj.contract is not None
