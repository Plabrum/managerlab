from app.actions.enums import ActionGroupType
from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    DatetimeFieldValue,
    EmailFieldValue,
    FieldType,
    IntFieldValue,
    ObjectColumn,
    StringFieldValue,
    URLFieldValue,
)


class BrandObject(BaseObject[Brand]):
    object_type = ObjectTypes.Brands

    @classmethod
    def model(cls) -> type[Brand]:
        return Brand

    @classmethod
    def title_field(cls, obj: Brand) -> str:
        return obj.name

    @classmethod
    def subtitle_field(cls, obj: Brand) -> str:
        return obj.description or ""

    # Action groups
    top_level_action_group = ActionGroupType.BrandActions
    action_group = ActionGroupType.BrandActions

    column_definitions = [
        ObjectColumn(
            key="id",
            label="ID",
            type=FieldType.Int,
            value=lambda obj: IntFieldValue(value=obj.id),
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="created_at",
            label="Created At",
            type=FieldType.Datetime,
            value=lambda obj: DatetimeFieldValue(value=obj.created_at),
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            value=lambda obj: DatetimeFieldValue(value=obj.updated_at),
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
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
            key="description",
            label="Description",
            type=FieldType.String,
            value=lambda obj: (StringFieldValue(value=obj.description) if obj.description else None),
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="website",
            label="Website",
            type=FieldType.URL,
            value=lambda obj: URLFieldValue(value=obj.website) if obj.website else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="phone",
            label="Phone",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.phone) if obj.phone else None,
            sortable=True,
            default_visible=True,
            editable=True,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="email",
            label="Email",
            type=FieldType.Email,
            value=lambda obj: EmailFieldValue(value=obj.email) if obj.email else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
    ]


class BrandContactObject(BaseObject[BrandContact]):
    object_type = ObjectTypes.BrandContacts

    @classmethod
    def model(cls) -> type[BrandContact]:
        return BrandContact

    @classmethod
    def title_field(cls, obj: BrandContact) -> str:
        return f"{obj.first_name} {obj.last_name}"

    @classmethod
    def subtitle_field(cls, obj: BrandContact) -> str:
        return obj.email or ""

    column_definitions = [
        ObjectColumn(
            key="full_name",
            label="Name",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=f"{obj.first_name} {obj.last_name}"),
            sortable=False,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="first_name",
            label="First Name",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.first_name),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="last_name",
            label="Last Name",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.last_name),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="email",
            label="Email",
            type=FieldType.Email,
            value=lambda obj: EmailFieldValue(value=obj.email) if obj.email else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="phone",
            label="Phone",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.phone) if obj.phone else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="brand_id",
            label="Brand ID",
            type=FieldType.Int,
            value=lambda obj: IntFieldValue(value=obj.brand_id),
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
    ]
