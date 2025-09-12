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
