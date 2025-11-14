"""Cryptographic token utilities for magic links and invitations."""

import hashlib
import hmac
import secrets

from app.utils.configure import config

__all__ = [
    "generate_secure_token",
    "hash_token",
    "verify_token_hash",
    "sign_payload",
    "verify_payload_signature",
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
    """Hash a token using HMAC-SHA256 for database storage.

    Args:
        token: Plaintext token to hash

    Returns:
        Hexadecimal HMAC-SHA256 hash (64 characters)

    Note:
        We store HMAC hashes instead of plaintext tokens in the database
        so that if the database is compromised, tokens cannot be used
        directly. HMAC-SHA256 with a secret key provides protection against
        rainbow table attacks. The plaintext token is only sent via email
        and never stored anywhere.
    """
    secret = config.SECRET_KEY.encode()
    return hmac.new(secret, token.encode(), hashlib.sha256).hexdigest()


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


def sign_payload(payload: bytes, secret: str) -> str:
    """Sign a payload with HMAC-SHA256.

    Args:
        payload: Raw bytes to sign (e.g., request body)
        secret: Secret key for HMAC signing

    Returns:
        Hexadecimal HMAC-SHA256 hash (64 characters)

    Note:
        Generic payload signing function for webhooks and API signatures.
        Use verify_payload_signature() to verify the signature.
    """
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def verify_payload_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify payload signature using constant-time comparison.

    Args:
        payload: Raw bytes that were signed
        signature: Signature to verify (hexadecimal string)
        secret: Secret key used for signing

    Returns:
        True if signature is valid, False otherwise

    Note:
        Uses `hmac.compare_digest()` to prevent timing attacks.
        Generic verification for webhook and API signatures.
    """
    computed_signature = sign_payload(payload, secret)
    return hmac.compare_digest(computed_signature, signature)
