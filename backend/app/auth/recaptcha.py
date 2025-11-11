"""reCAPTCHA v3 verification service."""

import aiohttp
from litestar.exceptions import ValidationException

from app.utils.configure import config

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
MIN_RECAPTCHA_SCORE = 0.5


class RecaptchaService:
    """Service for verifying reCAPTCHA v3 tokens."""

    def __init__(self, http_client: aiohttp.ClientSession) -> None:
        self.http_client = http_client

    async def verify_token(self, token: str) -> None:
        """Verify a reCAPTCHA v3 token with Google's API.

        Raises:
            ValidationException: If verification fails or score is too low
        """
        # Skip verification if no secret key configured (development)
        if not config.RECAPTCHA_SECRET_KEY:
            return

        data = aiohttp.FormData()
        data.add_field("secret", config.RECAPTCHA_SECRET_KEY)
        data.add_field("response", token)

        async with self.http_client.post(
            RECAPTCHA_VERIFY_URL,
            data=data,
            timeout=aiohttp.ClientTimeout(total=10.0),
        ) as response:
            result = await response.json()

            if not result.get("success") or result.get("score", 0.0) < MIN_RECAPTCHA_SCORE:
                raise ValidationException(detail="Verification failed. Please try again.")
