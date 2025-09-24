"""Action framework models."""

from typing import TYPE_CHECKING, Any, Dict
from abc import ABC, abstractmethod

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import BaseDBModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.objects.models.base import BaseObject


class ActionLog(BaseDBModel):
    """Audit log for action executions."""

    __tablename__ = "action_logs"

    object_type: Mapped[str] = mapped_column(sa.String(50), nullable=False, index=True)
    object_id: Mapped[int] = mapped_column(sa.Integer, nullable=False, index=True)
    action_name: Mapped[str] = mapped_column(sa.String(100), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    object_version: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(
        sa.String(255), nullable=True, index=True
    )
    context: Mapped[Dict[str, Any] | None] = mapped_column(sa.JSON, nullable=True)
    result: Mapped[Dict[str, Any] | None] = mapped_column(sa.JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    success: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    execution_time_ms: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)


class BaseAction(ABC):
    """Base class for all actions."""

    # These should be overridden in subclasses
    action_name: str
    label: str
    priority: int = 100

    @abstractmethod
    async def is_available(
        self,
        session: "AsyncSession",
        obj: "BaseObject",
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> bool:
        """Determine if this action is available for the given object and user."""
        pass

    @abstractmethod
    async def perform(
        self,
        session: "AsyncSession",
        obj: "BaseObject",
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Perform the action.

        Returns a dictionary with:
        - new_state: Optional[str] - if the action changed the object's state
        - updated_fields: Optional[Dict[str, Any]] - fields that were updated
        - result: Any - action-specific result data
        """
        pass

    def __lt__(self, other: "BaseAction") -> bool:
        """Sort by priority then name."""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.action_name < other.action_name
