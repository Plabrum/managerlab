from __future__ import annotations
from typing import Any, Optional, Literal
import datetime as dt
import decimal
from litestar.dto import DTOConfig
import msgspec
import sqlalchemy as sa
from sqlalchemy.orm import Mapper
from litestar.dto.base_dto import AbstractDTO

# ------------ helpers


def _maybe_optional(tp: Any, nullable: bool) -> Any:
    if not nullable:
        return tp
    return Optional[tp]  # type: ignore[valid-type]


def _sa_column_to_pytype(col: sa.Column[Any]) -> Any:
    t = col.type
    # Common concrete SQLA types first
    if isinstance(t, (sa.Integer, sa.BigInteger, sa.SmallInteger)):
        return int
    if isinstance(t, (sa.Float, sa.REAL)):
        return float
    if isinstance(t, sa.Numeric):
        return decimal.Decimal
    if isinstance(
        t,
        (
            sa.String,
            sa.Text,
            sa.LargeBinary,
            sa.Unicode,
            sa.UnicodeText,
            sa.CHAR,
            sa.VARCHAR,
        ),
    ):
        return str
    if isinstance(t, sa.Boolean):
        return bool
    if isinstance(t, sa.Date):
        return dt.date
    if isinstance(t, (sa.DateTime, sa.TIMESTAMP)):
        return dt.datetime
    if isinstance(t, sa.Time):
        return dt.time
    if isinstance(t, sa.Enum):
        # If bound to a Python Enum, use that; else fall back to str
        py_enum = getattr(t, "enum_class", None)
        return py_enum or str
    if isinstance(t, sa.JSON):
        return Any  # could be dict/array—keep it loose
    # Unknown/driver-specific → Any
    return Any


def _snake_to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _apply_rename(field: str, cfg: DTOConfig) -> str:
    rs = getattr(cfg, "rename_strategy", None)
    if rs and str(rs).lower().endswith("camel"):
        return _snake_to_camel(field)
    return field


def _pk_pytype(mapper: Mapper) -> Any:
    """Return the Python type for a model's primary key."""
    pks = list(mapper.primary_key)
    if not pks:
        return Any
    # Assume a single-column PK, which is true for 99% of cases
    col = pks[0]
    return _sa_column_to_pytype(col)  # type: ignore[arg-type]


# ------------ main converter

# Cache to prevent creating duplicate struct types
_struct_cache: dict[tuple[type, str | None, str], type[msgspec.Struct]] = {}


def dto_to_msgspec_struct_from_mapper(
    dto_cls: type[AbstractDTO[Any]],
    *,
    name: str | None = None,
    include_relationships: Literal["skip", "ids", "nested"] = "skip",
) -> type[msgspec.Struct]:
    """
    Build a msgspec.Struct from a concrete SQLAlchemyDTO[...] without using typing.get_type_hints.

    - Columns come from SQLAlchemy mapper/columns
    - Types are inferred from SQLA column types
    - Applies DTOConfig include/exclude and rename_strategy
    - Relationships:
        - "skip": ignore relationships (default)
        - "ids": include related object's PK type (or list[...] for uselist)
        - "nested": include `Any` (or list[Any]) placeholders for full nested data
    """
    # Create cache key from DTO class, name, and relationship mode
    cache_key = (dto_cls, name, include_relationships)
    if cache_key in _struct_cache:
        return _struct_cache[cache_key]

    try:
        model = dto_cls.model_type
    except Exception:
        breakpoint()
    cfg: DTOConfig = getattr(dto_cls, "config", DTOConfig())
    mapper: Mapper = sa.inspect(model)  # type: ignore[assignment]

    # 1) Start with columns
    fields: dict[str, Any] = {}
    for col in mapper.columns:
        py_t = _sa_column_to_pytype(col)
        fields[str(col.key)] = _maybe_optional(py_t, nullable=bool(col.nullable))

    # 2) Optionally add relationships
    if include_relationships != "skip":
        for rel in mapper.relationships:  # type: RelationshipProperty
            key = str(rel.key)
            if include_relationships == "ids":
                target_pk_t = _pk_pytype(rel.mapper)
                t = target_pk_t
                if rel.uselist:
                    t = list[target_pk_t]  # type: ignore[valid-type]
                # relationships are typically optional on write
                fields[key] = Optional[t]  # type: ignore[valid-type]
            elif include_relationships == "nested":
                t = Any
                if rel.uselist:
                    t = list[Any]  # type: ignore[index]
                fields[key] = Optional[t]  # type: ignore[valid-type]

    # 3) Apply DTO include/exclude (match *original* ORM attribute names)
    include = set(getattr(cfg, "include", set()) or set())
    exclude = set(getattr(cfg, "exclude", set()) or set())
    if include:
        fields = {k: v for k, v in fields.items() if k in include}
    if exclude:
        fields = {k: v for k, v in fields.items() if k not in exclude}

    # 4) Rename keys to match wire format if needed
    wire_fields = {_apply_rename(k, cfg): v for k, v in fields.items()}

    # 5) Build msgspec struct - convert dict to list of (name, type) tuples
    # Use DTO class's fully qualified name to ensure uniqueness
    if name:
        struct_name = name
    else:
        dto_module = dto_cls.__module__.replace(".", "_")
        dto_class_name = dto_cls.__name__
        struct_name = f"{dto_module}_{dto_class_name}_Schema"

    field_list = [(name, typ) for name, typ in wire_fields.items()]
    struct = msgspec.defstruct(struct_name, field_list)

    # Cache the result to prevent duplicate struct creation
    _struct_cache[cache_key] = struct
    return struct


def update_model(object, update_vals):
    """Update an existing model instance from a DTO/struct, skipping None values."""
    for field, value in update_vals.__dict__.items():
        if value is not None:
            setattr(object, field, value)


def create_model(model_class: type, create_vals) -> Any:
    """Create a new model instance from a CreateDTO/struct.

    Args:
        model_class: The SQLAlchemy model class to instantiate
        create_vals: A DTO or msgspec.Struct containing the values

    Returns:
        A new instance of model_class with fields populated from create_vals
    """
    # Convert struct/DTO to dict, filtering out None values
    data = {
        field: value
        for field, value in create_vals.__dict__.items()
        if value is not None
    }
    return model_class(**data)
