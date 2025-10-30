from litestar import Request, Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.auth.guards import requires_user_id
from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact
from app.brands.objects import BrandContactObject, BrandObject
from app.brands.schemas import (
    BrandContactSchema,
    BrandContactUpdateSchema,
    BrandSchema,
    BrandUpdateSchema,
)

# Register BrandObject and BrandContactObject with the objects framework
from app.objects.base import ObjectRegistry
from app.objects.enums import ObjectTypes
from app.threads.models import Thread
from app.utils.db import get_or_404, update_model
from app.utils.sqids import Sqid

ObjectRegistry().register(ObjectTypes.Brands, BrandObject)
ObjectRegistry().register(ObjectTypes.BrandContacts, BrandContactObject)


@get("/{id:str}")
async def get_brand(
    id: Sqid,
    request: Request,
    transaction: AsyncSession,
    action_registry: ActionRegistry,
) -> BrandSchema:
    """Get a brand by SQID."""
    from sqlalchemy.orm import joinedload, selectinload

    brand = await get_or_404(
        transaction,
        Brand,
        id,
        load_options=[
            joinedload(Brand.thread).options(
                selectinload(Thread.messages),
                selectinload(Thread.read_statuses),
            )
        ],
    )

    # Compute actions for this brand
    action_group = action_registry.get_class(ActionGroupType.BrandActions)
    actions = action_group.get_available_actions(obj=brand)

    # Convert thread to unread info using the mixin method
    thread_info = brand.get_thread_unread_info(request.user)

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
        actions=actions,
        thread=thread_info,
    )


@post("/{id:str}")
async def update_brand(id: Sqid, data: BrandUpdateSchema, request: Request, transaction: AsyncSession) -> BrandSchema:
    """Update a brand by SQID."""
    brand = await get_or_404(transaction, Brand, id)
    await update_model(
        session=transaction,
        model_instance=brand,
        update_vals=data,
        user_id=request.user,
        team_id=brand.team_id,
    )
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
        actions=[],  # Update endpoints don't compute actions
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
    id: Sqid,
    data: BrandContactUpdateSchema,
    request: Request,
    transaction: AsyncSession,
) -> BrandContactSchema:
    """Update a brand contact by SQID."""
    contact = await get_or_404(transaction, BrandContact, id)
    await update_model(
        session=transaction,
        model_instance=contact,
        update_vals=data,
        user_id=request.user,
        team_id=contact.team_id,
    )
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
