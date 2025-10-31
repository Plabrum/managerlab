from enum import Enum
from typing import Any

from sqlalchemy import types
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


class TextEnum[E: Enum](types.TypeDecorator[E]):
    """Store enum as TEXT, converting between enum and string."""

    impl = types.Text
    cache_ok = True

    def __init__(self, enum_class: type[E], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value: E | None, dialect: Any) -> str | None:
        """Convert enum to string for database."""
        if value is None:
            return None
        return value.name

    def process_result_value(self, value: str | None, dialect: Any) -> E | None:
        """Convert string from database to enum."""
        if value is None:
            return None
        return self.enum_class[value]


class _StateMachineMixinBase[E: Enum](BaseDBModel):
    __abstract__ = True
    state: Mapped[E]


def StateMachineMixin[E: Enum](*, state_enum: type[E], initial_state: E) -> type[_StateMachineMixinBase[E]]:
    class _StateMachineMixin(_StateMachineMixinBase[E]):
        __abstract__ = True

        @declared_attr
        def state(cls) -> Mapped[E]:
            return mapped_column(
                TextEnum(state_enum),
                index=True,
                nullable=False,
                default=initial_state,
                server_default=initial_state.name,
            )

        def __init_subclass__(cls, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)
            # Override the generic type annotation with the concrete enum type
            # This allows DTO introspection tools (msgspec) to properly resolve the enum
            if not cls.__dict__.get("__abstract__", False):
                cls.__annotations__["state"] = Mapped[state_enum]

    return _StateMachineMixin
