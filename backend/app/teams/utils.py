"""Team utility functions."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.crypto import generate_secure_token, hash_token
from app.auth.models import TeamInvitationToken
from app.utils.configure import config


def _build_invitation_link_url(token: str) -> str:
    """Build a complete invitation link URL.

    Args:
        token: Plaintext token to include in URL

    Returns:
        Complete URL for the team invitation

    Example:
        >>> _build_invitation_link_url("xyz789")
        'http://localhost:3000/invite/accept?token=xyz789'
    """
    base_url = config.FRONTEND_ORIGIN.rstrip("/")
    return f"{base_url}/invite/accept?token={token}"


async def generate_scoped_team_link(
    db_session: AsyncSession,
    team_id: int,
    invited_email: str,
    invited_by_user_id: int,
    expires_in_hours: int = 72,
) -> str:
    """
    Generate a secure, time-limited invitation link for joining a team.

    Args:
        db_session: Database session
        team_id: ID of the team to invite user to
        invited_email: Email address of the user being invited
        invited_by_user_id: ID of the user sending the invitation
        expires_in_hours: Number of hours until the link expires (default: 72 hours / 3 days)

    Returns:
        Full URL for the invitation link (e.g., https://tryarive.com/invite/accept?token=...)

    Note:
        This creates a TeamInvitationToken record in the database with a hashed token.
        The plaintext token is only returned in the URL and never stored.
    """
    # Generate secure token
    token = generate_secure_token()
    token_hash = hash_token(token)

    # Create invitation token record
    invitation_token = TeamInvitationToken.create_invitation(
        team_id=team_id,
        invited_email=invited_email.lower().strip(),
        invited_by_user_id=invited_by_user_id,
        token_hash=token_hash,
        expires_in_hours=expires_in_hours,
    )

    db_session.add(invitation_token)
    await db_session.flush()  # Flush to ensure token is created

    # Build and return the invitation URL
    return _build_invitation_link_url(token)


async def verify_team_invitation_token(
    db_session: AsyncSession,
    token: str,
) -> dict[str, int | str] | None:
    """
    Verify and decode a team invitation token.

    Args:
        db_session: Database session
        token: The invitation token to verify

    Returns:
        Dict containing 'team_id', 'invited_email', and 'invited_by_user_id' if valid,
        None if invalid or expired

    Note:
        This does NOT mark the token as accepted. That should be done separately
        after successfully creating the user and role.
    """
    token_hash = hash_token(token)

    # Find the token with pessimistic lock to prevent race conditions
    result = await db_session.execute(
        select(TeamInvitationToken)
        .where(TeamInvitationToken.token_hash == token_hash)
        .where(TeamInvitationToken.accepted_at.is_(None))
        .with_for_update()  # Prevent concurrent use of same token
    )
    invitation_token = result.scalar_one_or_none()

    if not invitation_token:
        return None

    # Check if valid (not expired, not accepted)
    if not invitation_token.is_valid():
        return None

    return {
        "team_id": invitation_token.team_id,
        "invited_email": invitation_token.invited_email,
        "invited_by_user_id": invitation_token.invited_by_user_id,
    }
