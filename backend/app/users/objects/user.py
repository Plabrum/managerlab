from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectListRequest,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.users.enums import UserStates
from app.users.models import User


class UserObject(BaseObject):
    object_type = ObjectTypes.Users
    model = User

    # Title/subtitle configuration
    title_field = "name"
    subtitle_field = "email"
    state_field = "state"

    column_definitions = [
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
            key="email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="email_verified",
            label="Email Verified",
            type=FieldType.Bool,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Bool),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="state",
            label="Status",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            available_values=[e.name for e in UserStates],
            editable=False,
            include_in_list=True,
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
