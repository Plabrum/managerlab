from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseAction, action_group_factory
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.brands.enums import BrandActions
from app.brands.models.brands import Brand
from app.brands.schemas import BrandUpdateSchema
from app.utils.db import update_model

# Create brand action group
brand_actions = action_group_factory(
    ActionGroupType.BrandActions,
    model_type=Brand,
)


@brand_actions
class DeleteBrand(BaseAction):
    action_key = BrandActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this brand?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls,
        obj: Brand,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted brand",
        )


@brand_actions
class UpdateBrand(BaseAction):
    action_key = BrandActions.update
    label = "Update"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Brand,
        data: BrandUpdateSchema,
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
            message="Updated brand",
        )
