from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import (
    ActionGroupType,
    BaseObjectAction,
    BaseTopLevelAction,
    action_group_factory,
)
from app.actions.base import EmptyActionData
from app.actions.deps import ActionDeps
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.brands.enums import BrandActions
from app.brands.models.brands import Brand
from app.brands.schemas import BrandCreateSchema, BrandUpdateSchema
from app.utils.db import create_model, update_model

# Create brand action group
brand_actions = action_group_factory(
    ActionGroupType.BrandActions,
    default_invalidation="/o/brands",
    model_type=Brand,
)


@brand_actions
class DeleteBrand(BaseObjectAction[Brand, EmptyActionData]):
    action_key = BrandActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this brand?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls, obj: Brand, data: EmptyActionData, transaction: AsyncSession, deps
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted brand",
        )


@brand_actions
class UpdateBrand(BaseObjectAction[Brand, BrandUpdateSchema]):
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
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=deps.user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated brand",
        )


@brand_actions
class CreateBrand(BaseTopLevelAction[BrandCreateSchema]):
    action_key = BrandActions.create
    label = "Create Brand"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: BrandCreateSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        new_brand = await create_model(
            session=transaction,
            team_id=deps.team_id,
            campaign_id=None,
            model_class=Brand,
            create_vals=data,
            user_id=deps.user,
        )
        return ActionExecutionResponse(
            message=f"Created brand '{new_brand.name}'",
        )
