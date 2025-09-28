from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_default_filters_for_field_type
from app.users.models import User
from app.utils.sqids import sqid_encode


class UserObject(BaseObject):
    object_type = ObjectTypes.User
    model = User
    column_definitions = [
        ColumnDefinitionDTO(
            key="name",
            label="Name",
            type=FieldType.String,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Email),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="email_verified",
            label="Email Verified",
            type=FieldType.Bool,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Bool),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created",
            type=FieldType.Datetime,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Datetime),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="updated_at",
            label="Updated",
            type=FieldType.Datetime,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Datetime),
            default_visible=False,
        ),
    ]

    @classmethod
    def to_detail_dto(cls, user: User) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=user.name,
                type=FieldType.String,
                label="Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="email",
                value=user.email,
                type=FieldType.Email,
                label="Email",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(user.id),
            object_type=ObjectTypes.User,
            state=user.state.name,
            fields=fields,
            actions=[],
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, user: User) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=user.name,
                type=FieldType.String,
                label="Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="email",
                value=user.email,
                type=FieldType.Email,
                label="Email",
                editable=False,
            ),
            ObjectFieldDTO(
                key="email_verified",
                value=user.email_verified,
                type=FieldType.Bool,
                label="Email Verified",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(user.id),
            object_type=ObjectTypes.User,
            title=user.name,
            subtitle=user.email,
            state=user.state.name,
            actions=[],
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
            fields=fields,
        )
