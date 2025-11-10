"""Cryptographic token utilities for magic links and invitations."""

import hashlib
import hmac
import secrets
from typing import Literal

from app.utils.configure import config

__all__ = [
    "generate_secure_token",
    "hash_token",
    "verify_token_hash",
    "build_magic_link_url",
    "build_invitation_link_url",
]


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token.

    Args:
        length: Number of random bytes to generate (default: 32)

    Returns:
        URL-safe base64-encoded token string

    Note:
        This uses `secrets.token_urlsafe()` which is suitable for
        security-sensitive applications like password reset tokens,
        authentication tokens, etc.
    """
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Hash a token using SHA-256 for database storage.

    Args:
        token: Plaintext token to hash

    Returns:
        Hexadecimal SHA-256 hash (64 characters)

    Note:
        We store hashes instead of plaintext tokens in the database
        so that if the database is compromised, tokens cannot be used
        directly. The plaintext token is only sent via email and never
        stored anywhere.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verify a token against its stored hash using constant-time comparison.

    Args:
        token: Plaintext token to verify
        token_hash: Stored hash to compare against

    Returns:
        True if token matches hash, False otherwise

    Note:
        Uses `hmac.compare_digest()` to prevent timing attacks. A timing
        attack could potentially allow an attacker to determine the hash
        one character at a time by measuring response times.
    """
    computed_hash = hash_token(token)
    return hmac.compare_digest(computed_hash, token_hash)


def build_magic_link_url(token: str, link_type: Literal["magic_link", "invitation"] = "magic_link") -> str:
    """Build a complete magic link URL.

    Args:
        token: Plaintext token to include in URL
        link_type: Type of link ("magic_link" or "invitation")

    Returns:
        Complete URL for the magic link or invitation

    Example:
        >>> build_magic_link_url("abc123", "magic_link")
        'http://localhost:3000/auth/magic-link/verify?token=abc123'
    """
    base_url = config.FRONTEND_ORIGIN.rstrip("/")

    if link_type == "magic_link":
        return f"{base_url}/auth/magic-link/verify?token={token}"
    else:
        return f"{base_url}/invite/accept?token={token}"


def build_invitation_link_url(token: str) -> str:
    """Build a complete invitation link URL.

    Args:
        token: Plaintext token to include in URL

    Returns:
        Complete URL for the team invitation

    Example:
        >>> build_invitation_link_url("xyz789")
        'http://localhost:3000/invite/accept?token=xyz789'
    """
    return build_magic_link_url(token, link_type="invitation")
