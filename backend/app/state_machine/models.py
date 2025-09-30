"""State machine models and framework."""

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


def StateMachineMixin[E: Enum](
    *,
    states: type[E],
    initial_state: E,
):
    class _StateMachineMixin(BaseDBModel):
        __abstract__ = True
        __state_enum__: type[E] = states  # app-layer can introspect this

        @declared_attr
        def _state_raw(cls) -> Mapped[str]:
            return mapped_column(
                "state",
                sa.Text,
                index=True,
                nullable=False,
                default=initial_state.name,
                server_default=initial_state.name,
            )

        @property
        def state(self) -> E:
            return states[self._state_raw]

        @state.setter
        def state(self, value: E) -> None:
            self._state_raw = value.name

    return _StateMachineMixin
