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
from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact
from app.utils.sqids import sqid_encode


class BrandObject(BaseObject):
    object_type = ObjectTypes.Brand

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
        return ObjectListDTO(
            id=sqid_encode(brand.id),
            object_type=ObjectTypes.Brand,
            title=brand.name,
            subtitle=brand.description,
            state="active",
            actions=[],
            created_at=brand.created_at.isoformat(),
            updated_at=brand.updated_at.isoformat(),
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        query = select(Brand)

        # Apply filters if provided
        if request.filters:
            if "name" in request.filters:
                query = query.where(Brand.name.ilike(f"%{request.filters['name']}%"))
            if "description" in request.filters:
                query = query.where(
                    Brand.description.ilike(f"%{request.filters['description']}%")
                )
            if "search" in request.filters:
                search_term = f"%{request.filters['search']}%"
                query = query.where(
                    (Brand.name.ilike(search_term))
                    | (Brand.description.ilike(search_term))
                )

        # Apply sorting
        if request.sort_by:
            sort_column = getattr(Brand, request.sort_by, None)
            if sort_column:
                if request.sort_order == "asc":
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
        else:
            # Default sort by created_at desc
            query = query.order_by(Brand.created_at.desc())

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> Brand:
        result = await session.get(Brand, object_id)
        if not result:
            raise ValueError(f"Brand with id {object_id} not found")
        return result

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[Brand], int]:
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        brands = result.scalars().all()

        return brands, total


class BrandContactObject(BaseObject):
    object_type = ObjectTypes.BrandContact

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
        return ObjectListDTO(
            id=sqid_encode(contact.id),
            object_type=ObjectTypes.BrandContact,
            title=full_name,
            subtitle=contact.email,
            state="active",
            actions=[],
            created_at=contact.created_at.isoformat(),
            updated_at=contact.updated_at.isoformat(),
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        query = select(BrandContact)

        # Apply filters if provided
        if request.filters:
            if "first_name" in request.filters:
                query = query.where(
                    BrandContact.first_name.ilike(f"%{request.filters['first_name']}%")
                )
            if "last_name" in request.filters:
                query = query.where(
                    BrandContact.last_name.ilike(f"%{request.filters['last_name']}%")
                )
            if "email" in request.filters:
                query = query.where(
                    BrandContact.email.ilike(f"%{request.filters['email']}%")
                )
            if "brand_id" in request.filters:
                query = query.where(
                    BrandContact.brand_id == request.filters["brand_id"]
                )
            if "search" in request.filters:
                search_term = f"%{request.filters['search']}%"
                query = query.where(
                    (BrandContact.first_name.ilike(search_term))
                    | (BrandContact.last_name.ilike(search_term))
                    | (BrandContact.email.ilike(search_term))
                )

        # Apply sorting
        if request.sort_by:
            sort_column = getattr(BrandContact, request.sort_by, None)
            if sort_column:
                if request.sort_order == "asc":
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
        else:
            # Default sort by last_name, then first_name
            query = query.order_by(
                BrandContact.last_name.asc(), BrandContact.first_name.asc()
            )

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> BrandContact:
        result = await session.get(BrandContact, object_id)
        if not result:
            raise ValueError(f"BrandContact with id {object_id} not found")
        return result

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[BrandContact], int]:
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        contacts = result.scalars().all()

        return contacts, total
