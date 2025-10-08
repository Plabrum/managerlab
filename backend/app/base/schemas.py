from typing import ClassVar, Literal
from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from msgspec import Struct
from app.base.models import BaseDBModel


class BaseSchema(Struct):
    pass


class SanitizedSQLAlchemyDTO[T: BaseDBModel](SQLAlchemyDTO[T]):
    config: ClassVar[SQLAlchemyDTOConfig] = SQLAlchemyDTOConfig(max_nested_depth=0)

    _BASE_EXCLUDE: ClassVar[set[str]] = {"id"}  # hide raw PK
    _BASE_RENAMES: ClassVar[dict[str, str]] = {
        "public_id": "id"
    }  # expose hashed id as "id"
    _BASE_INCLUDE_IMPLICIT: ClassVar[bool | Literal["hybrid-only"]] = "hybrid-only"

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        base_cfg = getattr(cls, "config", SQLAlchemyDTOConfig(max_nested_depth=0))

        # Decide mode based on whether include is provided by the subclass
        have_include = bool(base_cfg.include)

        max_depth = base_cfg.max_nested_depth
        include_implicit = (
            base_cfg.include_implicit_fields
            if base_cfg.include_implicit_fields is not None
            else cls._BASE_INCLUDE_IMPLICIT
        )
        rename_fields = {**cls._BASE_RENAMES, **(base_cfg.rename_fields or {})}

        if have_include:
            # Whitelist mode: never set exclude (pass empty), ensure public_id is present so rename -> "id" works
            include = base_cfg.include | {"public_id"}
            # If dotted paths are whitelisted and depth not set, allow one level
            if base_cfg.max_nested_depth is None and any(
                "." in f for f in include if isinstance(f, str)
            ):
                max_depth = 1
            exclude: frozenset[str] = frozenset()  # empty AbstractSet
        else:
            # Blacklist mode: don't set include; add raw id to exclude
            include = frozenset()  # empty AbstractSet
            exclude = frozenset(base_cfg.exclude) | cls._BASE_EXCLUDE

        cls.config = SQLAlchemyDTOConfig(
            include=include,
            exclude=exclude,
            rename_fields=rename_fields,
            include_implicit_fields=include_implicit,
            max_nested_depth=max_depth,
            # pass-through
            rename_strategy=base_cfg.rename_strategy,
            partial=base_cfg.partial,
            underscore_fields_private=base_cfg.underscore_fields_private,
            experimental_codegen_backend=base_cfg.experimental_codegen_backend,
            forbid_unknown_fields=base_cfg.forbid_unknown_fields,
        )


class UpdateSQLAlchemyDTO[T: BaseDBModel](SQLAlchemyDTO[T]):
    """Base DTO for partial updates - makes all fields optional and excludes read-only fields."""

    config: ClassVar[SQLAlchemyDTOConfig] = SQLAlchemyDTOConfig(
        partial=True,  # Makes all fields optional for updates
        max_nested_depth=0,  # Prevent deep nesting in updates
    )

    _BASE_EXCLUDE: ClassVar[set[str]] = {
        "id",
        "created_at",
        "updated_at",
        "public_id",
    }  # Exclude read-only fields
    _BASE_INCLUDE_IMPLICIT: ClassVar[bool | Literal["hybrid-only"]] = (
        False  # Don't include hybrid properties
    )

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        base_cfg = getattr(
            cls, "config", SQLAlchemyDTOConfig(partial=True, max_nested_depth=0)
        )

        # Always exclude read-only fields for updates
        exclude = base_cfg.exclude | cls._BASE_EXCLUDE

        # For updates, we typically don't need include/rename logic
        # Just use blacklist mode with partial=True
        cls.config = SQLAlchemyDTOConfig(
            partial=True,  # Always partial for updates
            exclude=exclude,
            max_nested_depth=base_cfg.max_nested_depth or 0,
            include_implicit_fields=cls._BASE_INCLUDE_IMPLICIT,
        )


class CreateSQLAlchemyDTO[T: BaseDBModel](SQLAlchemyDTO[T]):
    config: ClassVar[SQLAlchemyDTOConfig] = SQLAlchemyDTOConfig(
        max_nested_depth=0,
        partial=False,  # All required fields must be present
    )

    _BASE_EXCLUDE: ClassVar[set[str]] = {"id", "public_id", "created_at", "updated_at"}
    _BASE_INCLUDE_IMPLICIT: ClassVar[bool | Literal["hybrid-only"]] = False

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        base_cfg = getattr(cls, "config", SQLAlchemyDTOConfig(max_nested_depth=0))

        exclude = base_cfg.exclude | cls._BASE_EXCLUDE
        cls.config = SQLAlchemyDTOConfig(
            exclude=exclude,
            partial=False,
            max_nested_depth=base_cfg.max_nested_depth or 0,
            include_implicit_fields=cls._BASE_INCLUDE_IMPLICIT,
        )
