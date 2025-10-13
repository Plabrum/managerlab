from abc import abstractmethod
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


from app.base.models import BaseDBModel

# TODO PAL: Add Log Table
# class StateTransitionLog[E: Enum, M: BaseDBModel](BaseDBModel):
#     """Audit log for state transitions."""
#
#     __tablename__ = "state_transition_logs"
#
#     object_id: Mapped[int] = mapped_column(sa.Integer, nullable=False, index=True)
#     from_state: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
#     to_state: Mapped[str] = mapped_column(sa.String(100), nullable=False)
#     user_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
#     context: Mapped[Dict[str, Any] | None] = mapped_column(sa.JSON, nullable=True)
#


class _StateMachineBase[E: Enum](BaseDBModel):
    __abstract__ = True

    @classmethod
    @abstractmethod
    def __state_enum__(cls) -> type[E]: ...

    @classmethod
    @abstractmethod
    def __initial_state__(cls) -> E: ...

    @declared_attr
    def _state_raw(cls) -> Mapped[str]:
        init = cls.__initial_state__()
        return mapped_column(
            "state",
            sa.Text,
            index=True,
            nullable=False,
            default=init.name,
            server_default=init.name,
        )

    @property
    def state(self) -> E:
        return self.__state_enum__()[self._state_raw]

    @state.setter
    def state(self, value: E) -> None:
        self._state_raw = value.name


def StateMachineMixin[E: Enum](
    *, states: type[E], initial_state: E
) -> type[_StateMachineBase[E]]:
    class _StateMachineMixin(_StateMachineBase[E]):
        __abstract__ = True

        @classmethod
        def __state_enum__(cls) -> type[E]:
            return states

        @classmethod
        def __initial_state__(cls) -> E:
            return initial_state

    return _StateMachineMixin
