from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    BoolFieldValue,
    EmailFieldValue,
    EnumFieldValue,
    FieldType,
    ObjectColumn,
    StringFieldValue,
)
from app.users.enums import UserStates
from app.users.models import User


class UserObject(BaseObject[User]):
    object_type = ObjectTypes.Users

    @classmethod
    def model(cls) -> type[User]:
        return User

    @classmethod
    def title_field(cls, user: User) -> str:
        return user.name

    @classmethod
    def subtitle_field(cls, user: User) -> str:
        return user.email

    @classmethod
    def state_field(cls, user: User) -> str:
        return user.state

    column_definitions = [
        ObjectColumn(
            key="name",
            label="Name",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.name),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="email",
            label="Email",
            type=FieldType.Email,
            value=lambda obj: EmailFieldValue(value=obj.email),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="email_verified",
            label="Email Verified",
            type=FieldType.Bool,
            value=lambda obj: BoolFieldValue(value=obj.email_verified),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="state",
            label="Status",
            type=FieldType.Enum,
            value=lambda obj: EnumFieldValue(value=obj.state),
            sortable=True,
            default_visible=True,
            available_values=[e.name for e in UserStates],
            editable=False,
            include_in_list=True,
        ),
    ]
