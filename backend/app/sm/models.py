"""State machine models and framework."""

from typing import TYPE_CHECKING, Any, Dict, Generic, Type, TypeVar, Set
from enum import Enum
from abc import ABC

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import BaseDBModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.objects.models.base import BaseObject


# Type variables for generic state machine
E = TypeVar("E", bound=Enum)  # Enum type for states
M = TypeVar("M", bound="BaseObject")  # Model type for objects


class StateTransitionLog(BaseDBModel):
    """Audit log for state transitions."""

    __tablename__ = "state_transition_logs"

    object_type: Mapped[str] = mapped_column(sa.String(50), nullable=False, index=True)
    object_id: Mapped[int] = mapped_column(sa.Integer, nullable=False, index=True)
    from_state: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    to_state: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    user_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    context: Mapped[Dict[str, Any] | None] = mapped_column(sa.JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    success: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)


class MachineSpec(Generic[M, E]):
    """Specification for a state machine."""

    def __init__(
        self,
        enum_type: Type[E],
        model_type: Type[M],
        initial: E,
        name: str,
        states: Dict[E, Type["State[M, E]"]],
    ):
        self.enum_type = enum_type
        self.model_type = model_type
        self.initial = initial
        self.name = name
        self.states = states

    def get_state_class(self, state_value: E) -> Type["State[M, E]"]:
        """Get the state class for a given state value."""
        return self.states[state_value]


class State(Generic[M, E], ABC):
    """Base class for all states in a state machine."""

    # REQUIRED per concrete state class
    value: E
    transitions: Set[E] = set()

    def __init__(self, machine_spec: MachineSpec[M, E]):
        self.machine_spec = machine_spec

    async def can_leave(
        self, session: "AsyncSession", obj: M, to: E, ctx: Dict[str, Any] | None = None
    ) -> bool:
        """Hook on current state before leaving."""
        return True

    async def on_exit(
        self,
        session: "AsyncSession",
        obj: M,
        to_state_class: Type["State[M, E]"],
        ctx: Dict[str, Any] | None = None,
    ) -> None:
        """Hook on current state when exiting."""
        pass

    async def can_enter(
        self,
        session: "AsyncSession",
        obj: M,
        from_state_class: Type["State[M, E]"] | None,
        ctx: Dict[str, Any] | None = None,
    ) -> bool:
        """Guard on target state before entering."""
        return True

    async def on_enter(
        self,
        session: "AsyncSession",
        obj: M,
        from_state_class: Type["State[M, E]"] | None,
        ctx: Dict[str, Any] | None = None,
    ) -> None:
        """Hook on target state when entering."""
        pass
