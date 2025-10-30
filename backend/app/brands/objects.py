from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectListRequest,
    FieldType,
    ObjectColumn,
)
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
        ObjectColumn(
            key="id",
            label="ID",
            type=FieldType.Int,
            value=lambda obj: obj.id,
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="created_at",
            label="Created At",
            type=FieldType.Datetime,
            value=lambda obj: obj.created_at,
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            value=lambda obj: obj.updated_at,
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="name",
            label="Name",
            type=FieldType.String,
            value=lambda obj: obj.name,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="description",
            label="Description",
            type=FieldType.String,
            value=lambda obj: obj.description,
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
            value=lambda obj: obj.website,
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
            value=lambda obj: obj.phone,
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
            value=lambda obj: obj.email,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
    ]


class BrandContactObject(BaseObject):
    object_type = ObjectTypes.BrandContacts
    model = BrandContact

    # Title/subtitle configuration
    title_field = "full_name"
    subtitle_field = "email"

    column_definitions = [
        ObjectColumn(
            key="full_name",
            label="Name",
            type=FieldType.String,
            value=lambda obj: f"{obj.first_name} {obj.last_name}",
            sortable=False,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="first_name",
            label="First Name",
            type=FieldType.String,
            value=lambda obj: obj.first_name,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="last_name",
            label="Last Name",
            type=FieldType.String,
            value=lambda obj: obj.last_name,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="email",
            label="Email",
            type=FieldType.Email,
            value=lambda obj: obj.email,
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
            value=lambda obj: obj.phone,
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
            value=lambda obj: obj.brand_id,
            sortable=True,
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
