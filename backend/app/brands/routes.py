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
from app.auth.guards import requires_authenticated_user

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
    brand = await transaction.get(Brand, brand_id)
    if not brand:
        raise ValueError(f"Brand with id {id} not found")
    return brand


@post("/{id:str}", return_dto=BrandDTO)
async def update_brand(
    id: Sqid, data: BrandUpdateSchema, transaction: AsyncSession
) -> Brand:
    """Update a brand by SQID."""
    brand_id = sqid_decode(id)
    brand = await transaction.get(Brand, brand_id)
    if not brand:
        raise ValueError(f"Brand with id {id} not found")

    # Apply updates from DTO - partial=True means only provided fields are included
    for field, value in data.__dict__.items():
        if hasattr(brand, field):  # Only update existing model fields
            setattr(brand, field, value)

    await transaction.flush()
    return brand


@get("/contacts/{id:str}", return_dto=BrandContactDTO)
async def get_brand_contact(id: Sqid, transaction: AsyncSession) -> BrandContact:
    """Get a brand contact by SQID."""
    contact_id = sqid_decode(id)
    contact = await transaction.get(BrandContact, contact_id)
    if not contact:
        raise ValueError(f"BrandContact with id {id} not found")
    return contact


@post("/contacts/{id:str}", return_dto=BrandContactDTO)
async def update_brand_contact(
    id: Sqid, data: BrandContactUpdateSchema, transaction: AsyncSession
) -> BrandContact:
    """Update a brand contact by SQID."""
    contact_id = sqid_decode(id)
    contact = await transaction.get(BrandContact, contact_id)
    if not contact:
        raise ValueError(f"BrandContact with id {id} not found")

    # Apply updates from DTO - partial=True means only provided fields are included
    for field, value in data.__dict__.items():
        if hasattr(contact, field):  # Only update existing model fields
            setattr(contact, field, value)

    await transaction.flush()
    return contact


# Brand router
brand_router = Router(
    path="/brands",
    guards=[requires_authenticated_user],
    route_handlers=[
        get_brand,
        update_brand,
        get_brand_contact,
        update_brand_contact,
    ],
    tags=["brands"],
)
