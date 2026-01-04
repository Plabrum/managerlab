from datetime import datetime

from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
from app.threads.schemas import ThreadUnreadInfo
from app.utils.sqids import Sqid


class BrandSchema(BaseSchema):
    """Manual schema for Brand model."""

    id: Sqid
    name: str
    description: str | None
    website: str | None
    email: str | None
    phone: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    team_id: int | None
    actions: list[ActionDTO]
    thread: ThreadUnreadInfo | None = None


class BrandUpdateSchema(BaseSchema):
    """Declarative update schema for Brand - all fields required."""

    name: str
    description: str | None
    website: str | None
    email: str | None
    phone: str | None
    notes: str | None


class BrandCreateSchema(BaseSchema):
    """Schema for creating a Brand."""

    name: str
    description: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class BrandContactSchema(BaseSchema):
    """Manual schema for BrandContact model."""

    id: Sqid
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    notes: str | None
    brand_id: Sqid
    created_at: datetime
    updated_at: datetime
    team_id: Sqid | None
    actions: list[ActionDTO] = []  # TODO: Implement BrandContactActions when needed


class BrandContactUpdateSchema(BaseSchema):
    """Declarative update schema for BrandContact - all fields required."""

    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    notes: str | None
    brand_id: Sqid


class BrandContactCreateSchema(BaseSchema):
    """Schema for creating a BrandContact."""

    first_name: str
    last_name: str
    brand_id: Sqid
    email: str | None = None
    phone: str | None = None
    notes: str | None = None
