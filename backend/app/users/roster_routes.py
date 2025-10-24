from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import Roster
from app.users.schemas import RosterSchema, RosterUpdateSchema
from app.utils.sqids import Sqid
from app.auth.guards import requires_user_id
from app.utils.db import get_or_404, update_model
from app.actions.registry import ActionRegistry
from app.actions.enums import ActionGroupType


@get("/{id:str}")
async def get_roster(
    id: Sqid, transaction: AsyncSession, action_registry: ActionRegistry
) -> RosterSchema:
    """Get a roster member by SQID."""
    roster = await get_or_404(transaction, Roster, id)

    # Compute actions for this roster member
    action_group = action_registry.get_class(ActionGroupType.RosterActions)
    actions = action_group.get_available_actions(obj=roster)

    return RosterSchema(
        id=roster.id,
        name=roster.name,
        email=roster.email,
        phone=roster.phone,
        birthdate=roster.birthdate,
        instagram_handle=roster.instagram_handle,
        facebook_handle=roster.facebook_handle,
        tiktok_handle=roster.tiktok_handle,
        youtube_channel=roster.youtube_channel,
        profile_photo_id=roster.profile_photo_id,
        state=roster.state.name,
        created_at=roster.created_at,
        updated_at=roster.updated_at,
        team_id=roster.team_id,
        actions=actions,
    )


@post("/{id:str}")
async def update_roster(
    id: Sqid, data: RosterUpdateSchema, transaction: AsyncSession
) -> RosterSchema:
    """Update a roster member by SQID."""
    roster = await get_or_404(transaction, Roster, id)
    update_model(roster, data)
    await transaction.flush()
    return RosterSchema(
        id=roster.id,
        name=roster.name,
        email=roster.email,
        phone=roster.phone,
        birthdate=roster.birthdate,
        instagram_handle=roster.instagram_handle,
        facebook_handle=roster.facebook_handle,
        tiktok_handle=roster.tiktok_handle,
        youtube_channel=roster.youtube_channel,
        profile_photo_id=roster.profile_photo_id,
        state=roster.state.name,
        created_at=roster.created_at,
        updated_at=roster.updated_at,
        team_id=roster.team_id,
        actions=[],  # Update endpoints don't compute actions
    )


roster_router = Router(
    path="/roster",
    guards=[requires_user_id],
    route_handlers=[
        get_roster,
        update_roster,
    ],
    tags=["roster"],
)
