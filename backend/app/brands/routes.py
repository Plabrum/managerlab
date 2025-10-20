from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact
from app.brands.schemas import (
    BrandDTO,
    BrandUpdateSchema,
    BrandContactDTO,
    BrandContactUpdateSchema,
)
from app.utils.sqids import Sqid, sqid_decode
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model

# Register BrandObject and BrandContactObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.brands.objects import BrandObject, BrandContactObject

ObjectRegistry().register(ObjectTypes.Brands, BrandObject)
ObjectRegistry().register(ObjectTypes.BrandContacts, BrandContactObject)


@get("/{id:str}", return_dto=BrandDTO)
async def get_brand(id: Sqid, transaction: AsyncSession) -> Brand:
    """Get a brand by SQID."""
    brand_id = sqid_decode(id)
    return await get_or_404(transaction, Brand, brand_id)


@post("/{id:str}", return_dto=BrandDTO)
async def update_brand(
    id: Sqid, data: BrandUpdateSchema, transaction: AsyncSession
) -> Brand:
    """Update a brand by SQID."""
    brand_id = sqid_decode(id)
    brand = await get_or_404(transaction, Brand, brand_id)
    update_model(brand, data)
    await transaction.flush()
    return brand


@get("/contacts/{id:str}", return_dto=BrandContactDTO)
async def get_brand_contact(id: Sqid, transaction: AsyncSession) -> BrandContact:
    """Get a brand contact by SQID."""
    contact_id = sqid_decode(id)
    return await get_or_404(transaction, BrandContact, contact_id)


@post("/contacts/{id:str}", return_dto=BrandContactDTO)
async def update_brand_contact(
    id: Sqid, data: BrandContactUpdateSchema, transaction: AsyncSession
) -> BrandContact:
    """Update a brand contact by SQID."""
    contact_id = sqid_decode(id)
    contact = await get_or_404(transaction, BrandContact, contact_id)
    update_model(contact, data)
    await transaction.flush()
    return contact


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
