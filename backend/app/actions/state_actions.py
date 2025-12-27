from abc import ABC
from enum import StrEnum
from typing import ClassVar, Generic, TypeVar

from msgspec import Struct
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.base import BaseObjectAction
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.base.models import BaseDBModel

E = TypeVar("E", bound=StrEnum)
O = TypeVar("O", bound=BaseDBModel)


class UpdateStateData(Struct):
    """Data for updating an object's state."""

    new_state: str


class BaseUpdateStateAction(BaseObjectAction[O, UpdateStateData], ABC, Generic[O, E]):
    """Base class for state update actions via kanban drag-and-drop.

    Subclasses must set:
    - action_key: The action enum value
    - state_enum: The StrEnum class for valid states
    """

    label: ClassVar[str] = "Update Status"
    is_bulk_allowed: ClassVar[bool] = True
    priority: ClassVar[int] = 10
    icon: ClassVar[ActionIcon] = ActionIcon.edit
    is_hidden: ClassVar[bool] = True  # Hidden from dropdown, only used by kanban

    state_enum: ClassVar[type[E]]
    state_field: ClassVar[str] = "state"

    @classmethod
    async def execute(
        cls,
        obj: O,
        data: UpdateStateData,
        transaction: AsyncSession,
        deps,
    ) -> ActionExecutionResponse:
        # Validate new state exists in enum
        try:
            new_state = cls.state_enum[data.new_state]
        except KeyError:
            return ActionExecutionResponse(
                message=f"Invalid state: {data.new_state}",
            )

        # Update state field
        setattr(obj, cls.state_field, new_state)

        return ActionExecutionResponse(
            message=f"Updated status to {new_state.value}",
        )
