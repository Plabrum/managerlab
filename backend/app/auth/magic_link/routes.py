"""Magic link authentication routes."""

import logging

import aiohttp
from email_validator import EmailNotValidError, validate_email
from litestar import Response, Router, get, post
from litestar.connection import Request
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.status_codes import HTTP_302_FOUND, HTTP_400_BAD_REQUEST
from msgspec import Struct, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.enums import ScopeType
from app.auth.magic_link.services import MagicLinkService
from app.auth.recaptcha import RecaptchaService
from app.emails.service import EmailService
from app.utils.configure import config

logger = logging.getLogger(__name__)


class MagicLinkRequestSchema(Struct):
    """Schema for requesting a magic link."""

    email: str
    recaptcha_token: str
    honeypot: str = ""  # Should be empty - bots often fill this

    def __post_init__(self) -> None:
        """Validate email address format."""
        try:
            # Validate email format (without deliverability check for performance)
            validate_email(self.email, check_deliverability=False)
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {e}") from e


class MagicLinkResponseSchema(Struct):
    """Response schema for magic link request."""

    success: bool
    message: str


def provide_magic_link_service(
    transaction: AsyncSession,
    email_service: EmailService,
) -> MagicLinkService:
    """Provide the magic link service."""
    return MagicLinkService(transaction, email_service)


def provide_recaptcha_service(http_client: aiohttp.ClientSession) -> RecaptchaService:
    """Provide the reCAPTCHA service."""
    return RecaptchaService(http_client)


@post("/request", guards=[])
async def request_magic_link(
    data: MagicLinkRequestSchema,
    magic_link_service: MagicLinkService,
    recaptcha_service: RecaptchaService,
) -> MagicLinkResponseSchema:
    """Request a magic link to be sent to the provided email.

    Args:
        data: Request data containing email address, recaptcha token, and honeypot
        magic_link_service: Magic link service
        recaptcha_service: reCAPTCHA verification service

    Returns:
        Response indicating success (always returns success for security)

    Note:
        For security, this always returns success even if the user doesn't exist.
        This prevents email enumeration attacks where an attacker could determine
        which email addresses have accounts.

    Bot Protection:
        - reCAPTCHA v3: Verifies token with Google (score threshold: 0.5)
        - Honeypot: Hidden field that bots often fill (humans leave empty)
        - Disposable emails: Blocks temporary email domains
    """
    from litestar.exceptions import ValidationException

    from app.auth.disposable_emails import validate_email_not_disposable

    # 1. Check honeypot field (should be empty)
    if data.honeypot:
        logger.warning(f"Honeypot triggered for email: {data.email}")
        raise ValidationException(detail="Invalid request. Please try again.")

    # 2. Verify reCAPTCHA token
    await recaptcha_service.verify_token(data.recaptcha_token)

    # 3. Check for disposable email domains
    validate_email_not_disposable(data.email)

    # 4. Proceed with magic link creation
    result = await magic_link_service.create_and_send_magic_link(data.email)
    return MagicLinkResponseSchema(**result)


@get("/verify", guards=[])
async def verify_magic_link(
    request: Request,
    transaction: AsyncSession,
    magic_link_service: MagicLinkService,
    token: str,
) -> Response:
    """Verify a magic link token and create a session.

    Args:
        request: Litestar request object
        transaction: Database session
        magic_link_service: Magic link service
        token: The magic link token from URL query parameter

    Returns:
        Redirect response to frontend

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not token:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Missing token parameter",
        )

    # Verify the token and get the user
    user = await magic_link_service.verify_magic_link_token(token)

    if not user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid or expired magic link. Please request a new one.",
        )

    # Create secure session (same as Google OAuth)
    request.session["user_id"] = int(user.id)
    request.session["authenticated"] = True

    # Set initial scope - check for team membership first, then campaign access
    from app.campaigns.models import CampaignGuest
    from app.users.models import Role

    # Check if user has team membership
    team_stmt = select(Role).where(Role.user_id == user.id).limit(1)
    team_result = await transaction.execute(team_stmt)
    first_role = team_result.scalar_one_or_none()

    if first_role:
        # User has team access - set team scope
        request.session["scope_type"] = ScopeType.TEAM.value
        request.session["team_id"] = int(first_role.team_id)
        logger.info(f"User {user.id} logged in via magic link with team scope (team_id={first_role.team_id})")
    else:
        # Check if user has campaign guest access
        campaign_stmt = select(CampaignGuest).where(CampaignGuest.user_id == user.id).limit(1)
        campaign_result = await transaction.execute(campaign_stmt)
        first_guest = campaign_result.scalar_one_or_none()

        if first_guest:
            # User has campaign access - set campaign scope
            request.session["scope_type"] = ScopeType.CAMPAIGN.value
            request.session["campaign_id"] = int(first_guest.campaign_id)
            logger.info(
                f"User {user.id} logged in via magic link with campaign scope (campaign_id={first_guest.campaign_id})"
            )
        else:
            # User has no access - they'll need to be invited to a team or campaign
            logger.warning(f"User {user.id} logged in via magic link but has no team or campaign access")
            # Don't set scope - they'll see an error when trying to access resources

    # Redirect to frontend success page
    frontend_url = config.SUCCESS_REDIRECT_URL

    logger.info(f"User {user.id} logged in via magic link, redirecting to {frontend_url}")
    return Response(
        content="",
        status_code=HTTP_302_FOUND,
        headers={"Location": frontend_url},
    )


magic_link_router = Router(
    path="/magic-link",
    route_handlers=[
        request_magic_link,
        verify_magic_link,
    ],
    dependencies={
        "magic_link_service": Provide(provide_magic_link_service, sync_to_thread=False),
        "recaptcha_service": Provide(provide_recaptcha_service, sync_to_thread=False),
    },
    middleware=[
        RateLimitConfig(rate_limit=("minute", 3)).middleware,  # 3 requests per minute per IP
    ],
    tags=["auth"],
)
