from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import (
    ActionGroupType,
    BaseObjectAction,
    action_group_factory,
)
from app.actions.deps import ActionDeps
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.users.enums import UserActions
from app.users.models import User
from app.users.schemas import UserUpdateSchema
from app.utils.db import update_model

# Create user action group
user_actions = action_group_factory(
    ActionGroupType.UserActions,
    model_type=User,
)


@user_actions
class UpdateUser(BaseObjectAction[User, UserUpdateSchema]):
    action_key = UserActions.update
    label = "Edit"
    is_bulk_allowed = False
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    def is_available(cls, obj: User | None, deps: ActionDeps) -> bool:
        # Users can only edit their own profile
        return obj is not None and (obj.id == deps.user)

    @classmethod
    async def execute(
        cls,
        obj: User,
        data: UserUpdateSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=deps.user,
            team_id=None,  # Users are not team-scoped
        )

        return ActionExecutionResponse(
            message="Updated profile",
        )
