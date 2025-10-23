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
from app.utils.sqids import Sqid
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
    # id is already decoded from SQID string to int by msgspec
    return await get_or_404(transaction, Brand, id)


@post("/{id:str}", return_dto=BrandDTO)
async def update_brand(
    id: Sqid, data: BrandUpdateSchema, transaction: AsyncSession
) -> Brand:
    """Update a brand by SQID."""
    # id is already decoded from SQID string to int by msgspec
    brand = await get_or_404(transaction, Brand, id)
    update_model(brand, data)
    await transaction.flush()
    return brand


@get("/contacts/{id:str}", return_dto=BrandContactDTO)
async def get_brand_contact(id: Sqid, transaction: AsyncSession) -> BrandContact:
    """Get a brand contact by SQID."""
    # id is already decoded from SQID string to int by msgspec
    return await get_or_404(transaction, BrandContact, id)


@post("/contacts/{id:str}", return_dto=BrandContactDTO)
async def update_brand_contact(
    id: Sqid, data: BrandContactUpdateSchema, transaction: AsyncSession
) -> BrandContact:
    """Update a brand contact by SQID."""
    # id is already decoded from SQID string to int by msgspec
    contact = await get_or_404(transaction, BrandContact, id)
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
