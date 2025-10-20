from litestar import Router, get, Response
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_302_FOUND, HTTP_400_BAD_REQUEST
from litestar.connection import Request
from litestar.params import Parameter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import aiohttp
from msgspec import Struct

from app.auth.enums import ScopeType
from app.auth.google.services import GoogleOAuthService
from app.auth.google.models import GoogleOAuthAccount
import logging


logger = logging.getLogger(__name__)


class GoogleOAuthCallbackSchema(Struct):
    """Schema for Google OAuth callback query parameters."""

    code: str | None = None
    state: str | None = None
    error: str | None = None


class GoogleUserInfoResponseSchema(Struct):
    """Schema for Google user information response."""

    google_id: str
    email: str
    name: str
    picture: str | None
    user_id: int


def provide_google_oauth_service(
    transaction: AsyncSession,
    http_client: aiohttp.ClientSession,
) -> GoogleOAuthService:
    """Provide the Google OAuth service."""
    return GoogleOAuthService(transaction, http_client)


@get("/login", guards=[])
async def google_login(
    transaction: AsyncSession, oauth_service: GoogleOAuthService
) -> Response:
    """Initiate Google OAuth login flow."""
    # Generate authorization URL and state
    auth_url, state = oauth_service.generate_auth_url()

    # Store state in database for CSRF protection
    await oauth_service.store_oauth_state(transaction, state)

    # Redirect to Google OAuth
    return Response(
        content="", status_code=HTTP_302_FOUND, headers={"Location": auth_url}
    )


@get("/callback", guards=[])
async def google_callback(
    request: Request,
    transaction: AsyncSession,
    oauth_service: GoogleOAuthService,
    code: str | None = None,
    oauth_state_token: str | None = Parameter(query="state", default=None),
    error: str | None = None,
) -> Response:
    """Handle Google OAuth callback."""

    # Check for OAuth errors
    if error:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}",
        )

    if not code or not oauth_state_token:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Missing authorization code or state parameter",
        )

    # Verify state to prevent CSRF attacks
    oauth_state = await oauth_service.verify_oauth_state(transaction, oauth_state_token)
    if not oauth_state:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    # Exchange code for tokens
    tokens = await oauth_service.exchange_code_for_tokens(code)

    # Get user info from Google
    user_info = await oauth_service.get_user_info(tokens["access_token"])

    # Create or update user
    user = await oauth_service.create_or_update_user(transaction, user_info, tokens)

    # Create secure session
    request.session["user_id"] = user.id
    request.session["authenticated"] = True

    # Set initial scope - check for team membership first, then campaign access
    from app.users.models import Role
    from app.campaigns.models import CampaignGuest

    # Check if user has team membership
    team_stmt = select(Role).where(Role.user_id == user.id).limit(1)
    team_result = await transaction.execute(team_stmt)
    first_role = team_result.scalar_one_or_none()

    if first_role:
        # User has team access - set team scope
        request.session["scope_type"] = ScopeType.TEAM.value
        request.session["team_id"] = first_role.team_id
        logger.info(
            f"User {user.id} logged in with team scope (team_id={first_role.team_id})"
        )
    else:
        # Check if user has campaign guest access
        campaign_stmt = (
            select(CampaignGuest).where(CampaignGuest.user_id == user.id).limit(1)
        )
        campaign_result = await transaction.execute(campaign_stmt)
        first_guest = campaign_result.scalar_one_or_none()

        if first_guest:
            # User has campaign access - set campaign scope
            request.session["scope_type"] = ScopeType.CAMPAIGN.value
            request.session["campaign_id"] = first_guest.campaign_id
            logger.info(
                f"User {user.id} logged in with campaign scope (campaign_id={first_guest.campaign_id})"
            )
        else:
            # User has no access - they'll need to be invited to a team or campaign
            logger.warning(
                f"User {user.id} logged in but has no team or campaign access"
            )
            # Don't set scope - they'll see an error when trying to access resources

    # Redirect to frontend success page
    frontend_url = oauth_service.config.SUCCESS_REDIRECT_URL

    logger.info(f"User {user.id} logged in via Google OAuth, going to {frontend_url}")
    return Response(
        content="",
        status_code=HTTP_302_FOUND,
        headers={"Location": frontend_url},
    )


@get("/me")
async def get_current_user_google_info(
    request: Request, transaction: AsyncSession
) -> GoogleUserInfoResponseSchema:
    """Get current user's Google OAuth information."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    stmt = select(GoogleOAuthAccount).where(GoogleOAuthAccount.user_id == user_id)
    result = await transaction.execute(stmt)
    google_account = result.scalar_one_or_none()

    if not google_account:
        raise HTTPException(
            status_code=404, detail="Google account not found for current user"
        )

    return GoogleUserInfoResponseSchema(
        google_id=google_account.google_id,
        email=google_account.email,
        name=google_account.name,
        picture=google_account.picture,
        user_id=google_account.user_id,
    )


google_auth_router = Router(
    path="/google",
    route_handlers=[
        google_login,
        google_callback,
        get_current_user_google_info,
    ],
    dependencies={
        "oauth_service": Provide(provide_google_oauth_service, sync_to_thread=False),
    },
    tags=["auth"],
)
