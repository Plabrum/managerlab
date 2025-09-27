from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
)
from app.campaigns.models import Campaign
from app.utils.sqids import sqid_encode


class CampaignObject(BaseObject):
    object_type = ObjectTypes.Campaign

    @classmethod
    def to_detail_dto(cls, campaign: Campaign) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=campaign.name,
                type=FieldType.String,
                label="Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="description",
                value=campaign.description,
                type=FieldType.Text,
                label="Description",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(campaign.id),
            object_type=ObjectTypes.Campaign,
            state="active",
            fields=fields,
            actions=[],
            created_at=campaign.created_at.isoformat(),
            updated_at=campaign.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, campaign: Campaign) -> ObjectListDTO:
        return ObjectListDTO(
            id=sqid_encode(campaign.id),
            object_type=ObjectTypes.Campaign,
            title=campaign.name,
            subtitle=campaign.description,
            state="active",
            actions=[],
            created_at=campaign.created_at.isoformat(),
            updated_at=campaign.updated_at.isoformat(),
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        query = select(Campaign)

        # Apply filters if provided
        if request.filters:
            if "name" in request.filters:
                query = query.where(Campaign.name.ilike(f"%{request.filters['name']}%"))
            if "description" in request.filters:
                query = query.where(
                    Campaign.description.ilike(f"%{request.filters['description']}%")
                )
            if "search" in request.filters:
                search_term = f"%{request.filters['search']}%"
                query = query.where(
                    (Campaign.name.ilike(search_term))
                    | (Campaign.description.ilike(search_term))
                )

        # Apply sorting
        if request.sort_by:
            sort_column = getattr(Campaign, request.sort_by, None)
            if sort_column:
                if request.sort_order == "asc":
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
        else:
            # Default sort by created_at desc
            query = query.order_by(Campaign.created_at.desc())

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> Campaign:
        result = await session.get(Campaign, object_id)
        if not result:
            raise ValueError(f"Campaign with id {object_id} not found")
        return result

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[Campaign], int]:
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        campaigns = result.scalars().all()

        return campaigns, total
