"""Team utility functions."""

from app.utils.configure import config


def generate_scoped_team_link(team_id: int, invited_email: str, expires_in_hours: int = 72) -> str:
    """
    Generate a secure, time-limited invitation link for joining a team.

    Args:
        team_id: ID of the team to invite user to
        invited_email: Email address of the user being invited
        expires_in_hours: Number of hours until the link expires (default: 72 hours / 3 days)

    Returns:
        Full URL for the invitation link (e.g., https://tryarive.com/invite/accept?token=...)

    TODO: Implement actual token generation with cryptographic signing.
    For now, returns a placeholder URL.
    """
    # TODO: Use a proper signing library to create secure tokens
    # For now, just create a placeholder URL for testing the email flow
    base_url = config.FRONTEND_ORIGIN
    placeholder_token = f"stub_token_team{team_id}_email{invited_email.replace('@', '_at_')}"
    return f"{base_url}/invite/accept?token={placeholder_token}"


def verify_team_invitation_token(token: str, max_age_hours: int = 72) -> dict[str, int | str]:
    """
    Verify and decode a team invitation token.

    Args:
        token: The invitation token to verify
        max_age_hours: Maximum age of token in hours (default: 72 hours / 3 days)

    Returns:
        Dict containing 'team_id' and 'email' if valid

    Raises:
        ValueError: If the token is invalid or tampered with

    TODO: Implement actual token verification with cryptographic signing.
    For now, raises NotImplementedError.
    """
    # TODO: Implement actual token verification
    raise NotImplementedError("Token verification not yet implemented - stub only")
