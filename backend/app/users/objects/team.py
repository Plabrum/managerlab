from typing import Sequence
from litestar import Request
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

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
    StringFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.users.models import Team, Role
from app.users.enums import RoleLevel
from app.utils.sqids import sqid_encode


class TeamObject(BaseObject):
    object_type = ObjectTypes.Teams
    model = Team
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
            key="description",
            label="Description",
            type=FieldType.Text,
            sortable=False,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
    ]

    @classmethod
    def to_detail_dto(cls, team: Team) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=StringFieldValue(value=team.name),
                label="Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="description",
                value=StringFieldValue(value=team.description or ""),
                label="Description",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(team.id),
            object_type=ObjectTypes.Teams,
            state="active",  # Teams don't have a state machine, so we use a default value
            title=team.name,
            fields=fields,
            actions=[],
            created_at=team.created_at,
            updated_at=team.updated_at,
            relations=[],
        )

    @classmethod
    async def to_list_dto(cls, team: Team) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=StringFieldValue(value=team.name),
                label="Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="description",
                value=StringFieldValue(value=team.description or ""),
                label="Description",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(team.id),
            object_type=ObjectTypes.Teams,
            title=team.name,
            subtitle=team.description,
            state="active",  # Teams don't have a state machine, so we use a default value
            actions=[
                ActionDTO(action="delete", label="Delete", is_bulk_allowed=False),
            ],
            created_at=team.created_at,
            updated_at=team.updated_at,
            fields=fields,
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        query = select(Team)

        # Apply structured filters and sorts using FilterMapper
        query = cls.apply_request_to_query(query, Team, request)

        # Default sort if no sorts applied
        if not request.sorts:
            query = query.order_by(Team.created_at.desc())

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> Team:
        result = await session.get(Team, object_id)
        if not result:
            raise ValueError(f"Team with id {object_id} not found")
        return result

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[Team], int]:
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        teams = result.scalars().all()

        return teams, total

    @classmethod
    async def can_delete(
        cls, team: Team, request: Request, transaction: AsyncSession
    ) -> bool:
        """Check if the current user can delete this team."""
        user_id = request.user
        if not user_id:
            return False

        # Query the user's role for this team
        stmt = select(Role).where(
            Role.user_id == user_id,
            Role.team_id == team.id,
        )
        result = await transaction.execute(stmt)
        role = result.scalar_one_or_none()

        # Only owners can delete teams
        return role is not None and role.role_level == RoleLevel.OWNER

    @classmethod
    async def delete(
        cls, team: Team, request: Request, transaction: AsyncSession
    ) -> None:
        """Soft delete a team. Only owners can delete teams."""
        if not await cls.can_delete(team, request, transaction):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Only team owners can delete teams",
            )

        team.soft_delete()
        transaction.add(team)
