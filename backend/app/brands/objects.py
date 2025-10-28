from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectListRequest,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact


class BrandObject(BaseObject):
    object_type = ObjectTypes.Brands
    model = Brand

    # Title/subtitle configuration
    title_field = "name"
    subtitle_field = "description"

    # Action groups
    top_level_action_group = ActionGroupType.TopLevelBrandActions
    action_group = ActionGroupType.BrandActions

    column_definitions = [
        ColumnDefinitionDTO(
            key="id",
            label="ID",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=False,
            include_in_list=False,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
            include_in_list=False,
        ),
        ColumnDefinitionDTO(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
            include_in_list=False,
        ),
        ColumnDefinitionDTO(
            key="name",
            label="Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="description",
            label="Description",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="website",
            label="Website",
            type=FieldType.URL,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.URL),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="phone",
            label="Phone",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=True,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Email),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
    ]


class BrandContactObject(BaseObject):
    object_type = ObjectTypes.BrandContacts
    model = BrandContact

    # Custom title generation
    subtitle_field = "email"

    @classmethod
    def to_list_dto(cls, obj: BrandContact):
        dto = super().to_list_dto(obj)
        # Generate full name for title
        dto.title = f"{obj.first_name} {obj.last_name}"
        return dto

    column_definitions = [
        ColumnDefinitionDTO(
            key="first_name",
            label="First Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="last_name",
            label="Last Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Email),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="phone",
            label="Phone",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="brand_id",
            label="Brand ID",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=False,
            include_in_list=False,
        ),
    ]

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
