"""Top-level actions for brands (actions that don't operate on specific brand instances)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseAction, action_group_factory
from app.actions.enums import ActionIcon
from app.brands.enums import BrandActions
from app.brands.models.brands import Brand
from app.brands.objects import BrandObject
from app.brands.schemas import BrandCreateSchema
from app.utils.db import create_model

# Create brand action group
top_level_brand_actions = action_group_factory(
    ActionGroupType.TopLevelBrandActions,
    model_type=Brand,
    object_service=BrandObject,
)


@top_level_brand_actions
class CreateBrand(BaseAction):
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
        team_id: int,
        user: int,
    ) -> Brand:
        new_brand = await create_model(
            session=transaction,
            team_id=team_id,
            campaign_id=None,
            model_class=Brand,
            create_vals=data,
            user_id=user,
        )
        return new_brand
