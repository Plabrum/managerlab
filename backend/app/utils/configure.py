import json
import logging
import os
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

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


@runtime_checkable
class ConfigProtocol(Protocol):
    """Protocol defining the interface for all configuration classes.

    This allows dependency injection to accept any config type (DevelopmentConfig,
    ProductionConfig, TestConfig) without msgspec validation errors.
    """

    ENV: str
    SECRET_KEY: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    RECAPTCHA_SECRET_KEY: str
    GOOGLE_REDIRECT_URI: str
    SUCCESS_REDIRECT_URL: str
    S3_BUCKET: str
    SES_REGION: str
    SES_FROM_NAME: str
    SES_FROM_EMAIL: str
    SES_REPLY_TO_EMAIL: str
    EMAIL_TEMPLATES_DIR: str
    ALLOW_LOCAL_SES: bool
    WEBHOOK_SECRET: str
    SESSION_COOKIE_DOMAIN: str | None
    FRONTEND_ORIGIN: str
    MAX_UPLOAD_SIZE: int
    MAX_DOCUMENT_SIZE: int
    IS_SYSTEM_MODE: bool
    OPENAI_API_KEY: str
    OPENAI_ORG_ID: str | None
    OPENAI_MODEL: str
    LOG_LEVEL: str

    @property
    def IS_DEV(self) -> bool: ...

    @property
    def SES_CONFIGURATION_SET(self) -> str: ...

    @property
    def INBOUND_EMAILS_BUCKET(self) -> str: ...

    @property
    def ADMIN_DB_URL(self) -> str: ...

    @property
    def SQLALCHEMY_DB_URL(self) -> str: ...

    @property
    def DATABASE_URL(self) -> str: ...

    @property
    def ASYNC_DATABASE_URL(self) -> str: ...


@dataclass
class Config:
    """Base application configuration."""

    ENV: str = "development"

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

    # Webhook Configuration (for inbound email)
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

    # Session Configuration
    SESSION_COOKIE_DOMAIN: str | None = os.getenv("SESSION_COOKIE_DOMAIN", "localhost")

    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    # Upload Configuration
    MAX_UPLOAD_SIZE: int = 40 * 1024 * 1024  # 40MB in bytes (for media files)
    MAX_DOCUMENT_SIZE: int = 100 * 1024 * 1024  # 100MB in bytes (for documents)

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_ORG_ID: str | None = os.getenv("OPENAI_ORG_ID")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    IS_SYSTEM_MODE: bool = os.getenv("SYSTEM_MODE", "false").lower() == "true"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def IS_DEV(self) -> bool:
        """Check if running in development mode."""
        return self.ENV == "development"

    @property
    def SES_CONFIGURATION_SET(self) -> str:
        """SES configuration set name."""
        # Allow explicit override via env var
        if config_set := os.getenv("SES_CONFIGURATION_SET"):
            return config_set
        # Use manageros-production for local SES testing, manageros-dev otherwise
        return "manageros-production" if self.ALLOW_LOCAL_SES else "manageros-dev"

    @property
    def INBOUND_EMAILS_BUCKET(self) -> str:
        """S3 bucket for inbound emails - dynamically set based on environment."""
        return f"manageros-inbound-emails-{self.ENV}"

    def _build_database_url(
        self,
        user: str,
        password: str,
        driver: str = "",
        port: str | None = None,
        endpoint: str | None = None,
        db_name: str | None = None,
    ) -> str:
        """Build database URL with given credentials and optional driver."""
        endpoint = endpoint or os.getenv("DB_ENDPOINT", "localhost")
        port = port or os.getenv("DB_PORT", "5432")
        db_name = db_name or os.getenv("DB_NAME", "manageros")

        protocol = f"postgresql{driver}"
        return f"{protocol}://{user}:{password}@{endpoint}:{port}/{db_name}"

    @property
    def ADMIN_DB_URL(self) -> str:
        """Database URL for migrations (postgres/admin user with schema privileges).

        Used by Alembic for running migrations.
        """
        # Check for override
        if url := os.getenv("ADMIN_DB_URL") or os.getenv("DATABASE_URL"):
            return url

        admin_user = os.getenv("DB_ADMIN_USER", "postgres")
        admin_password = os.getenv("DB_ADMIN_PASSWORD", "postgres")
        return self._build_database_url(admin_user, admin_password)

    @property
    def SQLALCHEMY_DB_URL(self) -> str:
        """SQLAlchemy async database URL for application runtime (arive user with RLS enforced).

        Used by SQLAlchemy for all ORM database operations.
        Same as ADMIN_DB_URL but with +psycopg driver for async support.
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
        """Backwards compatibility - use ADMIN_DB_URL instead."""
        return self.ADMIN_DB_URL

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Backwards compatibility - use SQLALCHEMY_DB_URL instead."""
        return self.SQLALCHEMY_DB_URL


@dataclass
class DevelopmentConfig(Config):
    """Development environment configuration."""

    ENV: str = "development"


@dataclass
class TestConfig(Config):
    """Test environment configuration."""

    __test__ = False  # Tell pytest not to collect this as a test class

    ENV: str = "testing"

    # Test-specific defaults
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "test-webhook-secret-key")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "test-bucket")
    SESSION_COOKIE_DOMAIN: str | None = os.getenv("SESSION_COOKIE_DOMAIN", "localhost")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "test-client-id")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "test-client-secret")

    @property
    def ADMIN_DB_URL(self) -> str:
        """Database URL for migrations (postgres/admin user with schema privileges).

        Uses port 5433 (test database) with postgres user.
        """
        # Check for override
        if url := os.getenv("TEST_ADMIN_DB_URL") or os.getenv("ADMIN_DB_URL") or os.getenv("DATABASE_URL"):
            return url

        admin_user = os.getenv("DB_ADMIN_USER", "postgres")
        admin_password = os.getenv("DB_ADMIN_PASSWORD", "postgres")
        return self._build_database_url(admin_user, admin_password, port="5433")

    @property
    def SQLALCHEMY_DB_URL(self) -> str:
        """SQLAlchemy async database URL for tests (arive user with RLS enforced).

        Uses port 5433 (test database) with arive user.
        """
        # Check for override
        if (
            url := os.getenv("TEST_SQLALCHEMY_DB_URL")
            or os.getenv("SQLALCHEMY_DB_URL")
            or os.getenv("ASYNC_DATABASE_URL")
        ):
            return url

        app_user = os.getenv("DB_USER", "arive")
        app_password = os.getenv("DB_PASSWORD", "arive")
        return self._build_database_url(app_user, app_password, driver="+psycopg", port="5433")


@dataclass
class ProductionConfig(Config):
    """Production environment configuration."""

    ENV: str = "production"


def get_config() -> Config:
    """Get configuration based on environment variable."""
    env = os.getenv("ENV", "development")

    if env == "testing":
        return TestConfig()
    elif env == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()


# Global config instance
config = get_config()
