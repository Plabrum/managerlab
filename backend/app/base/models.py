from datetime import datetime
from typing import Any, Dict, Set, Type, TYPE_CHECKING

from sqlalchemy import DateTime, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func

from app.utils.sqids import sqid_encode

if TYPE_CHECKING:
    from app.actions.schemas import ActionDTO


class BaseDBModel(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    # Registry to track all model classes
    _model_registry: Set[Type["BaseDBModel"]] = set()

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    def __init_subclass__(cls, **kwargs):
        """Automatically register model classes when they're defined."""
        super().__init_subclass__(**kwargs)
        # Only register models that have a __tablename__ (actual table models)
        if hasattr(cls, "__tablename__"):
            BaseDBModel._model_registry.add(cls)

    @classmethod
    def get_all_models(cls) -> Set[Type["BaseDBModel"]]:
        """Get all registered model classes."""
        return cls._model_registry

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    @hybrid_property
    def public_id(self) -> str:
        return sqid_encode(self.id)

    @property
    def actions(self) -> list["ActionDTO"]:
        """Get available actions for this object instance."""
        from app.actions.registry import ActionRegistry

        registry = ActionRegistry()  # Gets singleton instance
        return registry.get_actions_for_instance(self)
