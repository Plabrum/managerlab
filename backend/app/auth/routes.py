"""Authentication-related routes and user management."""

from litestar import Request, Router, post, get
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.enums import ScopeType
from app.auth.google.routes import google_auth_router
from app.auth.guards import requires_user_id
from app.auth.schemas import (
    TeamScopeSchema,
    CampaignScopeSchema,
    ListScopesResponse,
    SwitchScopeRequest,
)
from app.users.models import Role, Team
from app.campaigns.models import CampaignGuest, Campaign


@get("/list-scopes", guards=[requires_user_id])
async def list_scopes(
    request: Request, transaction: AsyncSession
) -> ListScopesResponse:
    """List all available scopes for the current user.

    Returns teams (via Role) and campaigns (via CampaignGuest) that the user has access to.
    """
    user_id: int = request.user

    # Get teams via Role table
    team_stmt = (
        select(Role, Team)
        .join(Team, Role.team_id == Team.id)
        .where(Role.user_id == user_id)
    )
    team_result = await transaction.execute(team_stmt)
    team_rows = team_result.all()

    teams = [
        TeamScopeSchema(
            team_id=role.team_id, team_name=team.name, role_level=role.role_level
        )
        for role, team in team_rows
    ]

    # Get campaigns via CampaignGuest table
    campaign_stmt = (
        select(CampaignGuest, Campaign, Team)
        .join(Campaign, CampaignGuest.campaign_id == Campaign.id)
        .join(Team, Campaign.team_id == Team.id)
        .where(CampaignGuest.user_id == user_id)
    )
    campaign_result = await transaction.execute(campaign_stmt)
    campaign_rows = campaign_result.all()

    campaigns = [
        CampaignScopeSchema(
            campaign_id=guest.campaign_id,
            campaign_name=campaign.name,
            team_id=campaign.team_id,
            team_name=team.name,
            access_level=guest.access_level,
        )
        for guest, campaign, team in campaign_rows
    ]

    # Get current scope from session
    current_scope_type = request.session.get("scope_type")
    current_scope_id = None
    if current_scope_type == ScopeType.TEAM.value:
        current_scope_id = request.session.get("team_id")
    elif current_scope_type == ScopeType.CAMPAIGN.value:
        current_scope_id = request.session.get("campaign_id")

    return ListScopesResponse(
        teams=teams,
        campaigns=campaigns,
        current_scope_type=current_scope_type,
        current_scope_id=current_scope_id,
    )


@post("/switch-scope", guards=[requires_user_id])
async def switch_scope(
    request: Request, data: SwitchScopeRequest, transaction: AsyncSession
) -> dict:
    """Switch the user's current scope.

    Validates that the user has access to the requested scope and updates the session.
    """
    user_id: int = request.user

    if data.scope_type == ScopeType.TEAM:
        # Verify user has access to this team via Role table
        stmt = select(Role).where(
            Role.user_id == user_id, Role.team_id == data.scope_id
        )
        result = await transaction.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"User does not have access to team {data.scope_id}",
            )

        # Update session
        request.session["scope_type"] = ScopeType.TEAM.value
        request.session["team_id"] = data.scope_id
        request.session.pop("campaign_id", None)  # Clear campaign_id

        return {"detail": "Switched to team scope", "team_id": data.scope_id}

    elif data.scope_type == ScopeType.CAMPAIGN:
        # Verify user has access to this campaign via CampaignGuest table
        campaign_stmt = select(CampaignGuest).where(
            CampaignGuest.user_id == user_id, CampaignGuest.campaign_id == data.scope_id
        )
        campaign_result = await transaction.execute(campaign_stmt)
        guest = campaign_result.scalar_one_or_none()

        if not guest:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"User does not have access to campaign {data.scope_id}",
            )

        # Update session
        request.session["scope_type"] = ScopeType.CAMPAIGN.value
        request.session["campaign_id"] = data.scope_id
        request.session.pop("team_id", None)  # Clear team_id

        return {"detail": "Switched to campaign scope", "campaign_id": data.scope_id}

    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Invalid scope_type: {data.scope_type}. Must be 'team' or 'campaign'",
        )


@post("/logout")
async def logout_user(request: Request) -> None:
    request.clear_session()


# Authentication router
auth_router = Router(
    path="/auth",
    route_handlers=[
        logout_user,
        list_scopes,
        switch_scope,
        google_auth_router,
    ],
    tags=["auth"],
)
