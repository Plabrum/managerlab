from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact
from app.brands.schemas import (
    BrandSchema,
    BrandUpdateSchema,
    BrandContactSchema,
    BrandContactUpdateSchema,
)
from app.utils.sqids import Sqid
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model

# Register BrandObject and BrandContactObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.brands.objects import BrandObject, BrandContactObject

ObjectRegistry().register(ObjectTypes.Brands, BrandObject)
ObjectRegistry().register(ObjectTypes.BrandContacts, BrandContactObject)


@get("/{id:str}")
async def get_brand(id: Sqid, transaction: AsyncSession) -> BrandSchema:
    """Get a brand by SQID."""
    brand = await get_or_404(transaction, Brand, id)
    return BrandSchema(
        id=brand.id,
        name=brand.name,
        description=brand.description,
        website=brand.website,
        email=brand.email,
        phone=brand.phone,
        notes=brand.notes,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
        team_id=brand.team_id,
    )


@post("/{id:str}")
async def update_brand(
    id: Sqid, data: BrandUpdateSchema, transaction: AsyncSession
) -> BrandSchema:
    """Update a brand by SQID."""
    brand = await get_or_404(transaction, Brand, id)
    update_model(brand, data)
    await transaction.flush()
    return BrandSchema(
        id=brand.id,
        name=brand.name,
        description=brand.description,
        website=brand.website,
        email=brand.email,
        phone=brand.phone,
        notes=brand.notes,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
        team_id=brand.team_id,
    )


@get("/contacts/{id:str}")
async def get_brand_contact(id: Sqid, transaction: AsyncSession) -> BrandContactSchema:
    """Get a brand contact by SQID."""
    contact = await get_or_404(transaction, BrandContact, id)
    return BrandContactSchema(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        notes=contact.notes,
        brand_id=contact.brand_id,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
        team_id=contact.team_id,
    )


@post("/contacts/{id:str}")
async def update_brand_contact(
    id: Sqid, data: BrandContactUpdateSchema, transaction: AsyncSession
) -> BrandContactSchema:
    """Update a brand contact by SQID."""
    contact = await get_or_404(transaction, BrandContact, id)
    update_model(contact, data)
    await transaction.flush()
    return BrandContactSchema(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        notes=contact.notes,
        brand_id=contact.brand_id,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
        team_id=contact.team_id,
    )


# Brand router
brand_router = Router(
    path="/brands",
    guards=[requires_user_id],
    route_handlers=[
        get_brand,
        update_brand,
        get_brand_contact,
        update_brand_contact,
    ],
    tags=["brands"],
)
