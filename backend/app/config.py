import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables once
load_dotenv(".env.local")


@dataclass
class Config:
    """Application configuration."""

    ENV: str = os.getenv("ENV", "development")
    IS_DEV: bool = ENV == "development"

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
    )
    SUCCESS_REDIRECT_URL: str = os.getenv(
        "SUCCESS_REDIRECT_URL", "http://localhost:3000/home"
    )
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")

    # Session Configuration
    SESSION_COOKIE_DOMAIN: str | None = os.getenv("SESSION_COOKIE_DOMAIN", None)

    @property
    def DATABASE_URL(self) -> str:
        """Sync database URL for migrations and sync operations."""
        # Check for full DATABASE_URL override first
        if database_url := os.getenv("DATABASE_URL"):
            return database_url

        # Default URLs based on environment
        if self.IS_DEV:
            return "postgresql://postgres:postgres@localhost:5432/manageros_dev"
        else:
            # Production default - get endpoint from environment
            db_endpoint = os.getenv("DB_ENDPOINT", "localhost")
            return f"postgresql://postgres:postgres@{db_endpoint}:5432/manageros"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Async database URL for application runtime with psycopg3."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")


# Global config instance
config = Config()
