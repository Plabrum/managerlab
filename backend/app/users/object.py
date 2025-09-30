from typing import Sequence, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ActionDTO,
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.users.enums import UserStates
from app.users.models import User
from app.utils.sqids import sqid_encode


class UserObject(BaseObject):
    object_type = ObjectTypes.Users
    model = User
    column_definitions = [
        ColumnDefinitionDTO(
            key="name",
            label="Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="email",
            label="Email",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="email_verified",
            label="Email verified",
            type=FieldType.Bool,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Bool),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="state",
            label="Status",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            available_values=[e.name for e in UserStates],
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
            object_type=ObjectTypes.Users,
            state=user.state.name,
            fields=fields,
            actions=[],
            created_at=user.created_at,
            updated_at=user.updated_at,
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
            ObjectFieldDTO(
                key="state",
                value=user.state.name,
                type=FieldType.Enum,
                label="Status",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(user.id),
            object_type=ObjectTypes.Users,
            title=user.name,
            subtitle=user.email,
            state=user.state.name,
            actions=[ActionDTO(action="edit", label="Edit")],
            created_at=user.created_at,
            updated_at=user.updated_at,
            fields=fields,
        )

    @classmethod
    def get_column_definitions(cls) -> List[ColumnDefinitionDTO]:
        """Get column definitions for user list views."""
        return [
            ColumnDefinitionDTO(
                key="name",
                label="Name",
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
                key="email_verified",
                label="Email Verified",
                type=FieldType.Bool,
                sortable=True,
                filter_type=get_filter_by_field_type(FieldType.Bool),
                default_visible=True,
            ),
            ColumnDefinitionDTO(
                key="created_at",
                label="Created",
                type=FieldType.Datetime,
                sortable=True,
                filter_type=get_filter_by_field_type(FieldType.Datetime),
                default_visible=True,
            ),
            ColumnDefinitionDTO(
                key="updated_at",
                label="Updated",
                type=FieldType.Datetime,
                sortable=True,
                filter_type=get_filter_by_field_type(FieldType.Datetime),
                default_visible=False,
            ),
        ]

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        query = select(User)

        # Apply structured filters and sorts using FilterMapper
        query = cls.apply_request_to_query(query, User, request)

        # Default sort if no sorts applied
        if not request.sorts:
            query = query.order_by(User.created_at.desc())

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> User:
        result = await session.get(User, object_id)
        if not result:
            raise ValueError(f"User with id {object_id} not found")
        return result

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[User], int]:
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        users = result.scalars().all()

        return users, total
