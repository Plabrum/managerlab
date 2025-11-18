from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from litestar import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.client.s3_client import BaseS3Client
from app.utils.configure import Config, TestConfig

# ============================================================================
# Mock Clients
# ============================================================================


@pytest.fixture
def mock_s3_client():
    """Provide a mocked S3 client for testing."""

    class TestS3Client(BaseS3Client):
        """Test S3 client that does nothing."""

        def download(self, local_path: str | Path, s3_key: str) -> None:
            pass

        def upload(self, local_path: str | Path, s3_key: str) -> None:
            pass

        def upload_fileobj(self, fileobj, s3_key: str) -> None:
            pass

        def generate_presigned_upload_url(self, key: str, content_type: str, expires_in: int = 300) -> str:
            return f"https://test-url.com/upload/{key}"

        def generate_presigned_download_url(self, key: str, expires_in: int = 3600) -> str:
            return f"https://test-url.com/download/{key}"

        def delete_file(self, key: str) -> None:
            pass

        def file_exists(self, key: str) -> bool:
            return True

        def get_file_bytes(self, key: str) -> bytes:
            return b"test file contents"

    return TestS3Client()


@pytest.fixture
def mock_http_client():
    """Provide a mocked HTTP client for testing."""
    return AsyncMock()


@pytest.fixture
def mock_email_client():
    """Provide a mocked email client for testing."""
    from app.emails.client import BaseEmailClient

    class TestEmailClient(BaseEmailClient):
        """Test email client that does nothing."""

        async def send_email(self, message) -> str:
            return "test-message-id"

    return TestEmailClient()


# ============================================================================
# Dependency Providers for Litestar DI
# ============================================================================


async def provide_test_transaction(db_session: AsyncSession, request: "Request") -> AsyncGenerator[AsyncSession]:
    """Test transaction provider for HTTP requests.

    Reads team_id from the session data (set by authenticated_client) and configures
    RLS context on the db_session.

    Note: We can't use the transaction fixture here due to Litestar DI circular dependency.
    Instead, we replicate the same RLS setup logic.
    """

    # Get team_id from session (set by authenticated_client fixture)
    team_id = request.session.get("team_id")

    if team_id:
        # Set team context and disable system mode for RLS enforcement
        await db_session.execute(text(f"SET LOCAL app.team_id = {team_id}"))
        await db_session.execute(text("SET LOCAL app.is_system_mode = false"))

    yield db_session

    # Restore system mode if we set it
    if team_id:
        try:
            await db_session.execute(text("SET LOCAL app.is_system_mode = true"))
        except Exception:
            pass  # Connection might be closed


def provide_test_config(test_config: TestConfig) -> Config:
    """Dependency provider for test config."""
    return test_config


def provide_test_team_id(team_id: int | None = None) -> int | None:
    """Dependency provider for team_id in tests."""
    return team_id


def provide_test_campaign_id(campaign_id: int | None = None) -> int | None:
    """Dependency provider for campaign_id in tests."""
    return campaign_id
