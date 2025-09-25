from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.objects.base import BaseObject
from app.objects.types import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
    StateDTO,
    ActionDTO,
)
from app.users.models.users import User
from app.utils.sqids import sqid_encode


class UserObject(BaseObject):
    object_type = ObjectTypes.User

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
            ObjectFieldDTO(
                key="email_verified",
                value=user.email_verified,
                type=FieldType.Bool,
                label="Email Verified",
                editable=False,
            ),
        ]

        state = StateDTO(
            key="active" if user.email_verified else "unverified",
            label="Active" if user.email_verified else "Unverified",
        )

        actions = [
            ActionDTO(action="edit", label="Edit User", priority=10),
            ActionDTO(
                action="verify_email",
                label="Verify Email",
                available=not user.email_verified,
                priority=20,
            ),
            ActionDTO(action="deactivate", label="Deactivate", priority=90),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(user.id),
            object_type=ObjectTypes.User,
            state=state,
            fields=fields,
            actions=actions,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, user: User) -> ObjectListDTO:
        state = StateDTO(
            key="active" if user.email_verified else "unverified",
            label="Active" if user.email_verified else "Unverified",
        )

        actions = [
            ActionDTO(action="edit", label="Edit", priority=10),
            ActionDTO(action="view", label="View", priority=1),
        ]

        return ObjectListDTO(
            id=sqid_encode(user.id),
            object_type=ObjectTypes.User,
            title=user.name,
            subtitle=user.email,
            state=state,
            actions=actions,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        query = select(User)

        # Apply filters if provided
        if request.filters:
            if "name" in request.filters:
                query = query.where(User.name.ilike(f"%{request.filters['name']}%"))
            if "email" in request.filters:
                query = query.where(User.email.ilike(f"%{request.filters['email']}%"))
            if "email_verified" in request.filters:
                query = query.where(
                    User.email_verified == request.filters["email_verified"]
                )
            if "search" in request.filters:
                search_term = f"%{request.filters['search']}%"
                query = query.where(
                    (User.name.ilike(search_term)) | (User.email.ilike(search_term))
                )

        # Apply sorting
        if request.sort_by:
            sort_column = getattr(User, request.sort_by, None)
            if sort_column:
                if request.sort_order == "asc":
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
        else:
            # Default sort by created_at desc
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

        # Get total count
        count_query = select(User)
        if request.filters:
            # Apply same filters for count
            if "name" in request.filters:
                count_query = count_query.where(
                    User.name.ilike(f"%{request.filters['name']}%")
                )
            if "email" in request.filters:
                count_query = count_query.where(
                    User.email.ilike(f"%{request.filters['email']}%")
                )
            if "email_verified" in request.filters:
                count_query = count_query.where(
                    User.email_verified == request.filters["email_verified"]
                )
            if "search" in request.filters:
                search_term = f"%{request.filters['search']}%"
                count_query = count_query.where(
                    (User.name.ilike(search_term)) | (User.email.ilike(search_term))
                )

        total_result = await session.execute(
            select(func.count()).select_from(count_query.subquery())
        )
        total = total_result.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        users = result.scalars().all()

        return users, total
