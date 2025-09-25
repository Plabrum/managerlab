"""Object schemas and DTOs."""

from enum import StrEnum, auto
from typing import Any, Dict, List, Optional

from app.base.schemas import BaseSchema


class FieldType(StrEnum):
    """Field types for object fields."""

    String = auto()
    Int = auto()
    Float = auto()
    Bool = auto()
    Date = auto()
    Datetime = auto()
    USD = auto()
    Email = auto()
    URL = auto()
    Text = auto()


class ObjectFieldDTO(BaseSchema):
    """DTO for object field representation."""

    key: str
    value: Any
    type: FieldType
    label: Optional[str] = None
    editable: bool = True


class StateDTO(BaseSchema):
    key: str
    label: str


class ActionDTO(BaseSchema):
    """DTO for action representation."""

    action: str
    label: str
    available: bool = True
    priority: int = 100


class ObjectRelationDTO(BaseSchema):
    """DTO for object relationships (parents/children)."""

    object_type: str
    sqid: str
    title: str


class ObjectDetailDTO(BaseSchema):
    """Detailed object representation."""

    id: str
    object_type: str
    state: StateDTO
    fields: List[ObjectFieldDTO]
    actions: List[ActionDTO]
    created_at: str
    updated_at: str
    children: List[Dict[str, ObjectRelationDTO]] = []
    parents: List[Dict[str, ObjectRelationDTO]] = []


class ObjectListDTO(BaseSchema):
    """Lightweight object representation for lists/tables."""

    id: str
    object_type: str
    title: str
    state: StateDTO
    created_at: str
    updated_at: str
    subtitle: Optional[str] = None
    actions: List[ActionDTO] = []


class ObjectListRequest(BaseSchema):
    """Request schema for listing objects."""

    limit: int = 50
    offset: int = 0
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"  # asc or desc


class ObjectListResponse(BaseSchema):
    """Response schema for object lists."""

    objects: List[ObjectListDTO]
    total: int
    limit: int
    offset: int
