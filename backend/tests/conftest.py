"""Pytest configuration and fixtures for backend tests."""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest

# Import and discover all models before tests run
from app.utils.discovery import discover_and_import

discover_and_import(["models.py", "models/**/*.py"], base_path="app")
from litestar import Litestar
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.config.cors import CORSConfig
from litestar.contrib.sqlalchemy.plugins import (
    AsyncSessionConfig,
    EngineConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from litestar.di import Provide
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.security.session_auth import SessionAuth
from litestar.stores.memory import MemoryStore
from litestar.testing import AsyncTestClient
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, StaticPool

# Import all route handlers
from app.actions.routes import action_router
from app.auth.enums import ScopeType
from app.auth.routes import auth_router
from app.base.models import BaseDBModel
from app.brands.routes import brand_router
from app.campaigns.routes import campaign_router
from app.dashboard.routes import dashboard_router
from app.deliverables.routes import deliverable_router
from app.documents.routes.documents import document_router
from app.media.routes import media_router
from app.objects.routes import object_router
from app.payments.routes import invoice_router
from app.roster.routes import roster_router
from app.threads import thread_router
from app.threads.websocket import thread_handler
from app.users.routes import public_user_router, user_router
from app.utils.configure import Config
from app.utils.db_filters import apply_soft_delete_filter


@pytest.fixture
def memory_store() -> MemoryStore:
    """Provide a fresh MemoryStore instance for each test."""
    return MemoryStore()


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Test database URL using PostgreSQL test database.

    Uses the same database as development but with a test schema.
    """
    return "postgresql+psycopg://postgres:postgres@localhost:5432/manageros_dev"


@pytest.fixture(scope="session")
def test_engine(test_db_url: str):
    """Create a test database engine for the entire test session."""
    engine = create_async_engine(
        test_db_url,
        echo=False,
        poolclass=StaticPool if ":memory:" in test_db_url else NullPool,
    )
    return engine


@pytest.fixture(scope="session")
def setup_database(test_engine):
    """Create all tables once at the start of the test session.

    This is intentionally synchronous to avoid async fixture issues.
    """
    import asyncio

    async def _setup():
        async with test_engine.begin() as conn:
            await conn.run_sync(BaseDBModel.metadata.create_all)

    async def _teardown():
        async with test_engine.begin() as conn:
            await conn.run_sync(BaseDBModel.metadata.drop_all)
        await test_engine.dispose()

    # Run setup
    asyncio.run(_setup())

    yield

    # Run teardown
    asyncio.run(_teardown())


@pytest.fixture
async def db_session(test_engine, setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for each test with automatic rollback.

    Each test gets an isolated transaction that is rolled back after the test,
    ensuring no test pollution.
    """
    session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autobegin=True,
    )

    async with session_maker() as session:
        async with session.begin():
            # Attach soft delete filter
            event.listen(session.sync_session, "do_orm_execute", apply_soft_delete_filter)

            yield session

            # Rollback happens automatically when context exits
            await session.rollback()

            # Remove listener
            event.remove(session.sync_session, "do_orm_execute", apply_soft_delete_filter)


# ============================================================================
# Test Configuration & Dependencies
# ============================================================================


@pytest.fixture
def test_config() -> Config:
    """Provide test configuration with safe defaults."""
    config = Config()
    config.ENV = "testing"
    config.IS_DEV = False
    config.S3_BUCKET = "test-bucket"
    config.SESSION_COOKIE_DOMAIN = "localhost"
    config.FRONTEND_ORIGIN = "http://localhost:3000"
    config.GOOGLE_CLIENT_ID = "test-client-id"
    config.GOOGLE_CLIENT_SECRET = "test-client-secret"
    return config


@pytest.fixture
def mock_s3_client():
    """Provide a mocked S3 client for testing."""
    mock = AsyncMock()
    mock.generate_presigned_url = AsyncMock(return_value="https://test-url.com/file")
    mock.upload_file = AsyncMock(return_value={"key": "test-key"})
    return mock


@pytest.fixture
def mock_http_client():
    """Provide a mocked HTTP client for testing."""
    return AsyncMock()


async def provide_test_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession]:
    """Test transaction provider that doesn't set RLS variables by default."""
    yield db_session


async def provide_test_transaction_with_rls(
    db_session: AsyncSession,
    team_id: int | None = None,
    campaign_id: int | None = None,
) -> AsyncGenerator[AsyncSession]:
    """Test transaction provider that sets RLS variables for team/campaign isolation testing."""
    # Set RLS variables if provided
    if team_id is not None:
        await db_session.execute(text(f"SET LOCAL app.team_id = {team_id}"))
    if campaign_id is not None:
        await db_session.execute(text(f"SET LOCAL app.campaign_id = {campaign_id}"))

    yield db_session


def provide_test_config(test_config: Config) -> Config:
    """Dependency provider for test config."""
    return test_config


def provide_test_team_id(team_id: int | None = None) -> int | None:
    """Dependency provider for team_id in tests."""
    return team_id


def provide_test_campaign_id(campaign_id: int | None = None) -> int | None:
    """Dependency provider for campaign_id in tests."""
    return campaign_id


# ============================================================================
# Litestar App Fixtures
# ============================================================================


@pytest.fixture
def route_handlers() -> list:
    """Provide all route handlers for the test app."""
    return [
        public_user_router,
        user_router,
        roster_router,
        auth_router,
        object_router,
        action_router,
        brand_router,
        campaign_router,
        deliverable_router,
        media_router,
        document_router,
        invoice_router,
        dashboard_router,
        thread_router,
        thread_handler,
    ]


@pytest.fixture
def test_app(
    route_handlers: list,
    test_config: Config,
    db_session: AsyncSession,
    mock_s3_client: Any,
    mock_http_client: Any,
    test_db_url: str,
) -> Litestar:
    """Create a Litestar app configured for testing.

    This fixture creates an app with:
    - All route handlers
    - Test database session
    - Mocked external dependencies (S3, HTTP)
    - Session authentication disabled by default (can be overridden)
    - In-memory stores for sessions and viewers
    """

    # Create session auth with test config
    session_auth = SessionAuth[int, Any](
        session_backend_config=ServerSideSessionConfig(
            samesite="lax",
            secure=False,  # Disable for testing
            httponly=True,
        ),
        retrieve_user_handler=lambda session, conn: session.get("user_id"),
        exclude=[
            "^/health",
            "^/auth/google/",
            "^/users/signup",
            "^/schema",
        ],
    )

    app = Litestar(
        route_handlers=route_handlers,
        middleware=[session_auth.middleware],
        on_app_init=[session_auth.on_app_init],
        cors_config=CORSConfig(
            allow_origins=[test_config.FRONTEND_ORIGIN],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        ),
        stores={
            "sessions": MemoryStore(),
            "viewers": MemoryStore(),
        },
        dependencies={
            "transaction": Provide(lambda: db_session, sync_to_thread=False),
            "http_client": Provide(lambda: mock_http_client, sync_to_thread=False),
            "config": Provide(lambda: test_config, sync_to_thread=False),
            "s3_client": Provide(lambda: mock_s3_client, sync_to_thread=False),
            "team_id": Provide(lambda: None, sync_to_thread=False),
            "campaign_id": Provide(lambda: None, sync_to_thread=False),
            "viewer_store": Provide(lambda: MemoryStore(), sync_to_thread=False),
        },
        plugins=[
            SQLAlchemyPlugin(
                config=SQLAlchemyAsyncConfig(
                    connection_string=test_db_url,
                    metadata=BaseDBModel.metadata,
                    engine_config=EngineConfig(
                        poolclass=StaticPool if ":memory:" in test_db_url else NullPool,
                    ),
                    session_config=AsyncSessionConfig(
                        expire_on_commit=False,
                        autoflush=False,
                        autobegin=True,
                    ),
                    create_all=False,  # We handle this in setup_database
                )
            ),
            ChannelsPlugin(
                backend=MemoryChannelsBackend(),
                arbitrary_channels_allowed=True,
            ),
        ],
        debug=True,  # Enable debug mode for better error messages in tests
    )

    return app


@pytest.fixture
async def test_client(
    test_app: Litestar,
) -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    """Provide an async test client for making HTTP requests.

    Usage:
        async def test_endpoint(test_client):
            response = await test_client.get("/health")
            assert response.status_code == 200
    """
    async with AsyncTestClient(app=test_app) as client:
        yield client


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
async def authenticated_client(
    test_client: AsyncTestClient[Litestar],
    db_session: AsyncSession,
) -> AsyncGenerator[tuple[AsyncTestClient[Litestar], dict[str, Any]], None]:
    """Provide an authenticated test client with a test user.

    Returns:
        Tuple of (client, user_data) where user_data contains user_id, team_id, etc.

    Usage:
        async def test_protected_endpoint(authenticated_client):
            client, user = authenticated_client
            response = await client.get("/users/me")
            assert response.json()["id"] == user["user_id"]
    """
    # Import factories here to avoid circular imports
    from tests.factories.users import TeamFactory, UserFactory

    # Create test user and team
    team = await TeamFactory.create_async(session=db_session, name="Test Team")
    user = await UserFactory.create_async(
        session=db_session,
        email="test@example.com",
        team_id=team.id,
    )

    await db_session.commit()

    # Set session data to authenticate
    await test_client.set_session_data(
        {
            "user_id": user.id,
            "team_id": team.id,
            "scope_type": ScopeType.TEAM.value,
        }
    )

    user_data = {
        "user_id": user.id,
        "team_id": team.id,
        "email": user.email,
        "team": team,
        "user": user,
    }

    yield test_client, user_data


@pytest.fixture
async def admin_client(
    test_client: AsyncTestClient[Litestar],
    db_session: AsyncSession,
) -> AsyncGenerator[tuple[AsyncTestClient[Litestar], dict[str, Any]], None]:
    """Provide an authenticated admin client for testing admin endpoints."""
    from tests.factories.users import TeamFactory, UserFactory

    team = await TeamFactory.create_async(session=db_session, name="Admin Team")
    admin = await UserFactory.create_async(
        session=db_session,
        email="admin@example.com",
        team_id=team.id,
        is_admin=True,
    )

    await db_session.commit()

    await test_client.set_session_data(
        {
            "user_id": admin.id,
            "team_id": team.id,
            "scope_type": ScopeType.TEAM.value,
        }
    )

    admin_data = {
        "user_id": admin.id,
        "team_id": team.id,
        "email": admin.email,
        "team": team,
        "user": admin,
    }

    yield test_client, admin_data


# ============================================================================
# RLS (Row-Level Security) Testing Fixtures
# ============================================================================


@pytest.fixture
async def multi_team_setup(
    db_session: AsyncSession,
) -> dict[str, Any]:
    """Create multiple teams and users for testing RLS isolation.

    Returns:
        Dict with team1, team2, user1, user2 for cross-team testing
    """
    from tests.factories.users import TeamFactory, UserFactory

    team1 = await TeamFactory.create_async(session=db_session, name="Team 1")
    team2 = await TeamFactory.create_async(session=db_session, name="Team 2")

    user1 = await UserFactory.create_async(
        session=db_session,
        email="user1@team1.com",
        team_id=team1.id,
    )
    user2 = await UserFactory.create_async(
        session=db_session,
        email="user2@team2.com",
        team_id=team2.id,
    )

    await db_session.commit()

    return {
        "team1": team1,
        "team2": team2,
        "user1": user1,
        "user2": user2,
    }
