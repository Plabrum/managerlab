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

    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-salt-key")

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # reCAPTCHA v3 Configuration
    RECAPTCHA_SECRET_KEY: str = os.getenv("RECAPTCHA_SECRET_KEY", "")

    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    SUCCESS_REDIRECT_URL: str = os.getenv("SUCCESS_REDIRECT_URL", "http://localhost:3000/")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")

    # Email Configuration (AWS SES)
    SES_REGION: str = os.getenv("SES_REGION", "us-east-1")
    SES_FROM_NAME: str = os.getenv("SES_FROM_NAME", "Arive")
    SES_FROM_EMAIL: str = os.getenv("SES_FROM_EMAIL", "noreply@tryarive.com")
    SES_REPLY_TO_EMAIL: str = os.getenv("SES_REPLY_TO_EMAIL", "support@tryarive.com")
    EMAIL_TEMPLATES_DIR: str = "templates/emails-react"  # React Email compiled templates
    ALLOW_LOCAL_SES: bool = os.getenv("ALLOW_LOCAL_SES", "false").lower() == "true"

    @property
    def SES_CONFIGURATION_SET(self) -> str:
        """SES configuration set name - uses manageros-production when ALLOW_LOCAL_SES is enabled."""
        # Allow explicit override via env var
        if config_set := os.getenv("SES_CONFIGURATION_SET"):
            return config_set
        # Use manageros-production for local SES testing, manageros-dev otherwise
        return "manageros-production" if self.ALLOW_LOCAL_SES else "manageros-dev"

    # Webhook Configuration (for inbound email)
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

    @property
    def INBOUND_EMAILS_BUCKET(self) -> str:
        """S3 bucket for inbound emails - dynamically set based on environment."""
        return f"manageros-inbound-emails-{self.ENV}"

    # Session Configuration
    SESSION_COOKIE_DOMAIN: str | None = os.getenv("SESSION_COOKIE_DOMAIN", "localhost")

    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    # Upload Configuration
    MAX_UPLOAD_SIZE: int = 40 * 1024 * 1024  # 40MB in bytes (for media files)
    MAX_DOCUMENT_SIZE: int = 100 * 1024 * 1024  # 100MB in bytes (for documents)

    IS_SYSTEM_MODE: bool = os.getenv("SYSTEM_MODE", "false").lower() == "true"

    def _build_database_url(self, user: str, password: str, driver: str = "") -> str:
        """Build database URL with given credentials and optional driver."""
        db_endpoint = os.getenv("DB_ENDPOINT", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "manageros")

        protocol = f"postgresql{driver}"
        return f"{protocol}://{user}:{password}@{db_endpoint}:{db_port}/{db_name}"

    @property
    def MIGRATION_DB_URL(self) -> str:
        """Database URL for migrations (postgres/admin user with schema privileges).

        Used by Alembic for running migrations.
        """
        # Check for override
        if url := os.getenv("MIGRATION_DB_URL") or os.getenv("DATABASE_URL"):
            return url

        admin_user = os.getenv("DB_ADMIN_USER", "postgres")
        admin_password = os.getenv("DB_ADMIN_PASSWORD", "postgres")
        return self._build_database_url(admin_user, admin_password)

    @property
    def APP_DB_URL(self) -> str:
        """Plain database URL for application runtime (arive user with RLS enforced).

        Used by: SAQ queue, channels backend, and other non-SQLAlchemy clients.
        """
        # Check for override
        if url := os.getenv("APP_DB_URL"):
            return url

        app_user = os.getenv("DB_USER", "arive")
        app_password = os.getenv("DB_PASSWORD", "arive")
        return self._build_database_url(app_user, app_password)

    @property
    def SQLALCHEMY_DB_URL(self) -> str:
        """SQLAlchemy async database URL for application runtime (arive user with RLS enforced).

        Used by SQLAlchemy for all ORM database operations.
        Same as APP_DB_URL but with +psycopg driver for async support.
        """
        # Check for override
        if url := os.getenv("SQLALCHEMY_DB_URL") or os.getenv("ASYNC_DATABASE_URL"):
            return url

        app_user = os.getenv("DB_USER", "arive")
        app_password = os.getenv("DB_PASSWORD", "arive")
        return self._build_database_url(app_user, app_password, driver="+psycopg")

    # Backwards compatibility aliases
    @property
    def DATABASE_URL(self) -> str:
        """Backwards compatibility - use MIGRATION_DB_URL instead."""
        return self.MIGRATION_DB_URL

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Backwards compatibility - use SQLALCHEMY_DB_URL instead."""
        return self.SQLALCHEMY_DB_URL


# Global config instance
config = Config()
