"""Litestar application and test client fixtures."""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from litestar import Litestar
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.di import Provide
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.stores.memory import MemoryStore
from litestar.testing import AsyncTestClient
from litestar_saq import TaskQueues
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.enums import ScopeType
from app.factory import create_app
from app.utils.configure import TestConfig
from app.utils.sqids import sqid_decode

from .dependencies import provide_test_transaction


@pytest.fixture
def test_app(
    test_config: TestConfig,
    db_session: AsyncSession,
    mock_s3_client: Any,
    mock_http_client: Any,
    mock_email_client: Any,
) -> Litestar:
    """Create a Litestar app configured for testing.

    The factory has production defaults. We override:
    - Dependencies: transaction, http_client, s3_client, email_client (mocks)
    - Plugins: StaticPool for DB, SAQ with in-memory queue, memory channels
    - Stores: MemoryStore for sessions

    SAQ tasks run synchronously and immediately during tests.
    """

    # Create provider functions that close over test fixtures
    # NOTE: We use provide_test_transaction to set RLS variables from session

    def provide_test_http_client() -> Any:
        return mock_http_client

    def provide_test_s3_client() -> Any:
        return mock_s3_client

    def provide_test_email_client() -> Any:
        return mock_email_client

    def provide_test_task_queues() -> Any:
        """Provide a TaskQueues object for testing."""
        # Create a mock queue
        mock_queue = Mock()
        mock_queue.enqueue = AsyncMock(return_value=None)

        # Create TaskQueues with default queue
        return TaskQueues({"default": mock_queue})

    def provide_shared_db_session() -> AsyncSession:
        """Provide the shared db_session from fixture."""
        return db_session

    # Create app with test-specific overrides
    app = create_app(
        config=test_config,
        # Override external service dependencies for testing
        dependencies_overrides={
            # Use shared db_session from fixture so all requests use same session
            "db_session": Provide(provide_shared_db_session, sync_to_thread=False),
            # Use test-specific transaction provider to properly set RLS variables from session
            "transaction": Provide(provide_test_transaction),
            "config": Provide(lambda: test_config, sync_to_thread=False),
            "http_client": Provide(provide_test_http_client, sync_to_thread=False),
            "s3_client": Provide(provide_test_s3_client, sync_to_thread=False),
            "email_client": Provide(provide_test_email_client, sync_to_thread=False),
            "task_queues": Provide(provide_test_task_queues, sync_to_thread=False),
        },
        # Override plugins for testing: memory channels only
        # SQLAlchemy plugin removed - we inject shared db_session via dependencies_overrides
        plugins_overrides=[
            # SAQ plugin removed for tests - background tasks not needed in unit tests
            ChannelsPlugin(
                backend=MemoryChannelsBackend(),
                arbitrary_channels_allowed=True,
            ),
        ],
        # Override stores for testing: MemoryStore for sessions
        stores_overrides={
            "sessions": MemoryStore(),
        },
    )

    return app


@pytest.fixture
async def test_client(
    test_app: Litestar,
) -> AsyncGenerator[AsyncTestClient[Litestar]]:
    """Provide an async test client for making HTTP requests.

    Usage:
        async def test_endpoint(test_client):
            response = await test_client.get("/health")
            assert response.status_code == 200
    """
    # Create session config for the test client
    session_config = ServerSideSessionConfig(
        samesite="lax",
        secure=False,
        httponly=True,
    )

    async with AsyncTestClient(app=test_app, session_config=session_config, raise_server_exceptions=True) as client:
        yield client

        # Clean up session data after each test to prevent leakage
        try:
            await client.set_session_data({})
        except Exception:
            # Ignore errors if session store is not available
            pass


@pytest.fixture
async def authenticated_client(
    test_client: AsyncTestClient[Litestar],
    user,
    team,
) -> AsyncGenerator[AsyncTestClient[Litestar]]:
    # Decode Sqid to integer for session storage
    user_id = sqid_decode(str(user.id))
    team_id = sqid_decode(str(team.id))

    await test_client.set_session_data(
        {
            "user_id": user_id,
            "team_id": team_id,
            "scope_type": ScopeType.TEAM.value,
        }
    )

    yield test_client
