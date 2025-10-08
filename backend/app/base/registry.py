from abc import ABC
from typing import Any, ClassVar, Dict, Self


class BaseRegistry[T, V](ABC):
    _instance: ClassVar[Self | None] = None
    _registry: Dict[T, V]
    dependencies: Dict[str, Any]

    def __new__(cls: type[Self], **dependencies: Any) -> Self:
        if cls._instance is None:
            inst = super().__new__(cls)
            # only initialize if the subclass hasn't provided its own already
            if not hasattr(inst, "_registry"):
                inst._registry = {}  # type: ignore[assignment]
            inst.dependencies = {}
            cls._instance = inst

        if dependencies:
            cls._instance.dependencies.update(dependencies)

        return cls._instance

    def register(self, key: T, value: V) -> None:
        self._registry[key] = value

    def get_class(self, key: T) -> V:
        if key not in self._registry:
            raise ValueError(
                f"Unknown object type: {key}, needed: {self._registry.keys()}"
            )
        return self._registry[key]

    def get_all_types(self) -> Dict[T, V]:
        return self._registry.copy()

    def is_registered(self, key: T) -> bool:
        return key in self._registry
