from datetime import datetime, timezone
from typing import Any, Dict, Set, Type, TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func

from app.utils.sqids import Sqid, SqidType

if TYPE_CHECKING:
    pass


class BaseDBModel(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    # Registry to track all model classes
    _model_registry: Set[Type["BaseDBModel"]] = set()

    id: Mapped[Sqid] = mapped_column(SqidType, primary_key=True, autoincrement=True)
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
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
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

    def soft_delete(self) -> None:
        """Soft delete this record by setting deleted_at timestamp."""
        self.deleted_at = datetime.now(tz=timezone.utc)

    def restore(self) -> None:
        """Restore a soft-deleted record by clearing deleted_at."""
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """Check if this record is soft-deleted."""
        return self.deleted_at is not None
