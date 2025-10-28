from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    StringFieldValue,
    URLFieldValue,
    EmailFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact
from app.utils.sqids import sqid_encode


class BrandObject(BaseObject):
    object_type = ObjectTypes.Brands
    model = Brand
    column_definitions = [
        ColumnDefinitionDTO(
            key="id",
            label="ID",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=False,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
        ),
        ColumnDefinitionDTO(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
        ),
        ColumnDefinitionDTO(
            key="name",
            label="Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="description",
            label="Description",
            type=FieldType.Text,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Text),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="website",
            label="Website",
            type=FieldType.URL,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.URL),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Email),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
        ),
    ]

    @classmethod
    def get_top_level_action_group(cls):
        return ActionGroupType.TopLevelBrandActions

    @classmethod
    def get_action_group(cls):
        return ActionGroupType.BrandActions

    @classmethod
    def to_list_dto(cls, brand: Brand) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=StringFieldValue(value=brand.name),
                label="Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="description",
                value=(
                    StringFieldValue(value=brand.description)
                    if brand.description
                    else None
                ),
                label="Description",
                editable=False,
            ),
            ObjectFieldDTO(
                key="website",
                value=URLFieldValue(value=brand.website) if brand.website else None,
                label="Website",
                editable=False,
            ),
            ObjectFieldDTO(
                key="phone",
                value=StringFieldValue(value=brand.phone) if brand.phone else None,
                label="Phone",
                editable=True,
            ),
            ObjectFieldDTO(
                key="email",
                value=EmailFieldValue(value=brand.email) if brand.email else None,
                label="Email",
                editable=False,
            ),
        ]

        # Get available actions for this brand
        action_group = ActionRegistry().get_class(ActionGroupType.BrandActions)
        actions = action_group.get_available_actions(obj=brand)

        return ObjectListDTO(
            id=sqid_encode(brand.id),
            object_type=ObjectTypes.Brands,
            title=brand.name,
            subtitle=brand.description,
            state="active",
            actions=actions,
            created_at=brand.created_at,
            updated_at=brand.updated_at,
            fields=fields,
        )


class BrandContactObject(BaseObject):
    object_type = ObjectTypes.BrandContacts
    model = BrandContact
    column_definitions = [
        ColumnDefinitionDTO(
            key="first_name",
            label="First Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="last_name",
            label="Last Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Email),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="phone",
            label="Phone",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="brand_id",
            label="Brand ID",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=False,
        ),
    ]

    @classmethod
    def to_list_dto(cls, contact: BrandContact) -> ObjectListDTO:
        full_name = f"{contact.first_name} {contact.last_name}"
        fields = [
            ObjectFieldDTO(
                key="first_name",
                value=StringFieldValue(value=contact.first_name),
                label="First Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="last_name",
                value=StringFieldValue(value=contact.last_name),
                label="Last Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="email",
                value=EmailFieldValue(value=contact.email) if contact.email else None,
                label="Email",
                editable=False,
            ),
            ObjectFieldDTO(
                key="phone",
                value=StringFieldValue(value=contact.phone) if contact.phone else None,
                label="Phone",
                editable=False,
            ),
        ]

        # BrandContactActions not implemented yet
        actions: list[Any] = []

        return ObjectListDTO(
            id=sqid_encode(contact.id),
            object_type=ObjectTypes.BrandContacts,
            title=full_name,
            subtitle=contact.email,
            state="active",
            actions=actions,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
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
