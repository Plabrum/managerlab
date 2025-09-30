"""Application package helpers."""

from importlib import import_module
from typing import Iterable


_MODEL_MODULES: tuple[str, ...] = (
    "app.auth.google.models",
    "app.brands.models.brands",
    "app.brands.models.contacts",
    "app.campaigns.models",
    "app.media.models",
    "app.payments.models",
    "app.posts.models",
    "app.sessions.models",
    "app.users.models",
)


def load_all_models(extra_modules: Iterable[str] | None = None) -> None:
    """Import all SQLAlchemy model modules to register mappers."""

    modules = _MODEL_MODULES
    if extra_modules:
        modules = (*_MODEL_MODULES, *tuple(extra_modules))

    for module_path in modules:
        import_module(module_path)


__all__ = ["load_all_models"]
