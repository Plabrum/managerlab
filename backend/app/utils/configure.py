import json
import logging
import os
from dataclasses import dataclass

import boto3
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables once
load_dotenv(".env.local")

# Load secrets from AWS Secrets Manager if running in AWS
# This must happen AFTER dotenv but BEFORE Config class instantiation
secret_arn = os.getenv("APP_SECRETS_ARN")
if secret_arn:
    # Create Secrets Manager client and fetch secrets
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secrets = json.loads(response["SecretString"])

    # Load all secrets into environment variables
    for key, value in secrets.items():
        if value:  # Only set non-empty values
            os.environ[key] = value

    logger.info(f"Loaded {len(secrets)} secrets from AWS Secrets Manager")


@dataclass
class Config:
    """Application configuration."""

    ENV: str = os.getenv("ENV", "development")
    IS_DEV: bool = ENV == "development"

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    SUCCESS_REDIRECT_URL: str = os.getenv("SUCCESS_REDIRECT_URL", "http://localhost:3000/")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")

    # Email Configuration (AWS SES)
    SES_REGION: str = os.getenv("SES_REGION", "us-east-1")
    SES_FROM_EMAIL: str = os.getenv("SES_FROM_EMAIL", "noreply@tryarive.com")
    SES_REPLY_TO_EMAIL: str = os.getenv("SES_REPLY_TO_EMAIL", "support@tryarive.com")
    SES_CONFIGURATION_SET: str = os.getenv("SES_CONFIGURATION_SET", "manageros-dev")
    EMAIL_TEMPLATES_DIR: str = "templates/emails"

    # Session Configuration
    SESSION_COOKIE_DOMAIN: str | None = os.getenv("SESSION_COOKIE_DOMAIN", "localhost")

    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    # Upload Configuration
    MAX_UPLOAD_SIZE: int = 40 * 1024 * 1024  # 40MB in bytes (for media files)
    MAX_DOCUMENT_SIZE: int = 100 * 1024 * 1024  # 100MB in bytes (for documents)

    IS_SYSTEM_MODE: bool = os.getenv("SYSTEM_MODE", "false").lower() == "true"

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

    @property
    def PSYCOPG_DATABASE_URL(self) -> str:
        """Plain psycopg database URL for psycopg-only clients (channels, direct connections)."""
        return self.DATABASE_URL  # Plain postgresql:// format without SQLAlchemy driver

    @property
    def QUEUE_DSN(self) -> str:
        """Queue DSN for SAQ (uses same database as application)."""
        # Check for override first
        if queue_dsn := os.getenv("QUEUE_DSN"):
            return queue_dsn
        # Use standard DATABASE_URL for queue
        return self.DATABASE_URL


# Global config instance
config = Config()
