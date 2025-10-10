from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Type, ClassVar, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.base.models import BaseDBModel
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse


class BaseAction(ABC):
    """Base class for all actions in the platform."""

    action_key: ClassVar[StrEnum]
    label: ClassVar[str]  # Display label
    is_bulk_allowed: ClassVar[bool] = False
    priority: ClassVar[int] = 100  # Display priority (lower = higher priority)
    icon: ClassVar[ActionIcon] = ActionIcon.default
    confirmation_message: ClassVar[str | None] = None  # Optional confirmation message

    # Model and load options for default get_object implementation
    model: ClassVar[Type[BaseDBModel] | None] = None
    load_options: ClassVar[list[ExecutableOption]] = []

    @classmethod
    async def get_object(
        cls,
        object_id: int,
        transaction: AsyncSession,
    ) -> BaseDBModel | None:
        if cls.model is None:
            return None

        result = await transaction.execute(
            select(cls.model)
            .where(cls.model.id == object_id)
            .options(*cls.load_options)
        )
        return result.scalar_one()

    @classmethod
    def is_available(
        cls,
        obj: BaseDBModel | None,
        **kwargs: Any,
    ) -> bool:
        return True

    @classmethod
    @abstractmethod
    async def execute(
        cls, obj: BaseDBModel | None, data: dict[str, Any], **kwargs: Any
    ) -> ActionExecutionResponse: ...
