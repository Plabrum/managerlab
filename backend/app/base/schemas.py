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
            exclude = frozenset()  # empty AbstractSet
        else:
            # Blacklist mode: don't set include; add raw id to exclude
            include = frozenset()  # empty AbstractSet
            exclude = base_cfg.exclude | cls._BASE_EXCLUDE

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
