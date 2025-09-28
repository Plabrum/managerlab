from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_default_filters_for_field_type
from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact
from app.utils.sqids import sqid_encode


class BrandObject(BaseObject):
    object_type = ObjectTypes.Brand
    model = Brand
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
            key="description",
            label="Description",
            type=FieldType.Text,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Text),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="website",
            label="Website",
            type=FieldType.URL,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.URL),
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
            key="created_at",
            label="Created",
            type=FieldType.Datetime,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Datetime),
            default_visible=False,
        ),
    ]

    @classmethod
    def to_detail_dto(cls, brand: Brand) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=brand.name,
                type=FieldType.String,
                label="Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="description",
                value=brand.description,
                type=FieldType.Text,
                label="Description",
                editable=True,
            ),
            ObjectFieldDTO(
                key="tone_of_voice",
                value=brand.tone_of_voice,
                type=FieldType.Text,
                label="Tone of Voice",
                editable=True,
            ),
            ObjectFieldDTO(
                key="brand_values",
                value=brand.brand_values,
                type=FieldType.Text,
                label="Brand Values",
                editable=True,
            ),
            ObjectFieldDTO(
                key="target_audience",
                value=brand.target_audience,
                type=FieldType.Text,
                label="Target Audience",
                editable=True,
            ),
            ObjectFieldDTO(
                key="website",
                value=brand.website,
                type=FieldType.URL,
                label="Website",
                editable=True,
            ),
            ObjectFieldDTO(
                key="email",
                value=brand.email,
                type=FieldType.Email,
                label="Email",
                editable=True,
            ),
            ObjectFieldDTO(
                key="phone",
                value=brand.phone,
                type=FieldType.String,
                label="Phone",
                editable=True,
            ),
            ObjectFieldDTO(
                key="notes",
                value=brand.notes,
                type=FieldType.Text,
                label="Notes",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(brand.id),
            object_type=ObjectTypes.Brand,
            state="active",
            fields=fields,
            actions=[],
            created_at=brand.created_at.isoformat(),
            updated_at=brand.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, brand: Brand) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=brand.name,
                type=FieldType.String,
                label="Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="description",
                value=brand.description,
                type=FieldType.Text,
                label="Description",
                editable=False,
            ),
            ObjectFieldDTO(
                key="website",
                value=brand.website,
                type=FieldType.URL,
                label="Website",
                editable=False,
            ),
            ObjectFieldDTO(
                key="email",
                value=brand.email,
                type=FieldType.Email,
                label="Email",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(brand.id),
            object_type=ObjectTypes.Brand,
            title=brand.name,
            subtitle=brand.description,
            state="active",
            actions=[],
            created_at=brand.created_at.isoformat(),
            updated_at=brand.updated_at.isoformat(),
            fields=fields,
        )


class BrandContactObject(BaseObject):
    object_type = ObjectTypes.BrandContact
    model = BrandContact
    column_definitions = [
        ColumnDefinitionDTO(
            key="first_name",
            label="First Name",
            type=FieldType.String,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="last_name",
            label="Last Name",
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
            key="phone",
            label="Phone",
            type=FieldType.String,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="brand_id",
            label="Brand ID",
            type=FieldType.Int,
            sortable=True,
            available_filters=get_default_filters_for_field_type(FieldType.Int),
            default_visible=False,
        ),
    ]

    @classmethod
    def to_detail_dto(cls, contact: BrandContact) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="first_name",
                value=contact.first_name,
                type=FieldType.String,
                label="First Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="last_name",
                value=contact.last_name,
                type=FieldType.String,
                label="Last Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="email",
                value=contact.email,
                type=FieldType.Email,
                label="Email",
                editable=True,
            ),
            ObjectFieldDTO(
                key="phone",
                value=contact.phone,
                type=FieldType.String,
                label="Phone",
                editable=True,
            ),
            ObjectFieldDTO(
                key="notes",
                value=contact.notes,
                type=FieldType.Text,
                label="Notes",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(contact.id),
            object_type=ObjectTypes.BrandContact,
            state="active",
            fields=fields,
            actions=[],
            created_at=contact.created_at.isoformat(),
            updated_at=contact.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, contact: BrandContact) -> ObjectListDTO:
        full_name = f"{contact.first_name} {contact.last_name}"
        fields = [
            ObjectFieldDTO(
                key="first_name",
                value=contact.first_name,
                type=FieldType.String,
                label="First Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="last_name",
                value=contact.last_name,
                type=FieldType.String,
                label="Last Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="email",
                value=contact.email,
                type=FieldType.Email,
                label="Email",
                editable=False,
            ),
            ObjectFieldDTO(
                key="phone",
                value=contact.phone,
                type=FieldType.String,
                label="Phone",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(contact.id),
            object_type=ObjectTypes.BrandContact,
            title=full_name,
            subtitle=contact.email,
            state="active",
            actions=[],
            created_at=contact.created_at.isoformat(),
            updated_at=contact.updated_at.isoformat(),
            fields=fields,
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        """Override default sorting for BrandContact."""

        query = select(cls.model)

        # Apply structured filters and sorts using helper method
        query = cls.apply_request_to_query(query, cls.model, request)

        # Custom default sort for contacts
        if not request.sorts:
            query = query.order_by(
                BrandContact.last_name.asc(), BrandContact.first_name.asc()
            )

        return query
