from datetime import datetime

from app.actions.schemas import ActionDTO
from app.base.schemas import BaseSchema
from app.users.enums import RoleLevel
from app.utils.sqids import Sqid


class UserSchema(BaseSchema):
    """Manual schema for User model."""

    id: Sqid
    name: str
    email: str
    email_verified: bool
    state: str
    created_at: datetime
    updated_at: datetime
    actions: list[ActionDTO]


class CreateUserSchema(BaseSchema):
    name: str
    email: str


class UserAndRoleSchema(BaseSchema):
    """Schema for a user with their role in a specific team context."""

    id: Sqid
    name: str
    email: str
    email_verified: bool
    state: str
    role_level: RoleLevel
    created_at: datetime
    updated_at: datetime


class UserUpdateSchema(BaseSchema):
    """Schema for updating a User."""

    name: str
