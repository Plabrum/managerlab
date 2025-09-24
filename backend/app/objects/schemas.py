"""Object schemas and DTOs."""

from typing import Any, Dict, List, Optional
from enum import Enum

from app.base.schemas import BaseSchema


class FieldType(str, Enum):
    """Field types for object fields."""

    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    DATE = "date"
    DATETIME = "datetime"
    USD = "usd"  # Currency field
    EMAIL = "email"
    URL = "url"
    TEXT = "text"  # Long text field


class ObjectFieldDTO(BaseSchema):
    """DTO for object field representation."""

    key: str
    value: Any
    type: FieldType
    label: Optional[str] = None
    editable: bool = True


class StateDTO(BaseSchema):
    """DTO for object state representation."""

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

    sqid: str
    object_type: str
    state: StateDTO
    object_version: int
    fields: List[ObjectFieldDTO]
    actions: List[ActionDTO]
    created_at: str
    updated_at: str
    children: List[Dict[str, ObjectRelationDTO]] = []
    parents: List[Dict[str, ObjectRelationDTO]] = []


class ObjectListDTO(BaseSchema):
    """Lightweight object representation for lists/tables."""

    sqid: str
    object_type: str
    title: str
    state: StateDTO
    created_at: str
    updated_at: str
    subtitle: Optional[str] = None
    actions: List[ActionDTO] = []


class PerformActionRequest(BaseSchema):
    """Request schema for performing actions."""

    action: str
    object_version: Optional[int] = None
    idempotency_key: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class PerformActionResult(BaseSchema):
    """Result schema for action execution."""

    success: bool
    result: Dict[str, Any]
    new_state: Optional[StateDTO] = None
    updated_fields: Optional[Dict[str, Any]] = None
    object_version: Optional[int] = None


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
