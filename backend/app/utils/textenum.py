"""TextEnum type decorator for SQLAlchemy.

This module provides a custom SQLAlchemy type that stores Python enums as TEXT
in the database, avoiding the complexity of PostgreSQL native ENUM types.
"""

from enum import Enum
from typing import Any

from sqlalchemy import types
from sqlalchemy.ext.compiler import compiles


class TextEnum[E: Enum](types.TypeDecorator[E]):
    """Store enum as TEXT, converting between enum and string.

    This avoids PostgreSQL ENUM type complexity when adding/removing values.
    For StrEnum types, values are stored as the enum's .value attribute (e.g., "active").
    For regular Enum types, values are stored as the enum's .name attribute (e.g., "ACTIVE").

    Example:
        class Status(StrEnum):
            DRAFT = auto()  # Stored as "draft"
            PUBLISHED = auto()  # Stored as "published"

        class Post(Base):
            status: Mapped[Status] = mapped_column(
                TextEnum(Status),
                nullable=False,
                default=Status.DRAFT,
            )
    """

    impl = types.Text
    cache_ok = True

    def __init__(self, enum_class: type[E], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value: E | str | None, dialect: Any) -> str | None:
        """Convert enum to string for database (stores enum name)."""
        if value is None:
            return None
        # Check for Enum BEFORE str, since StrEnum is both
        if isinstance(value, Enum):
            return value.name
        # SQLAlchemy relationship filters may pass strings directly
        return value

    def process_result_value(self, value: str | None, dialect: Any) -> E | None:
        """Convert string from database to enum."""
        if value is None:
            return None
        return self.enum_class[value]


@compiles(TextEnum, "postgresql")
def compile_text_enum(element: TextEnum, compiler: Any, **kw: Any) -> str:
    """Compile TextEnum to TEXT for PostgreSQL."""
    return "TEXT"
