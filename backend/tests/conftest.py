"""Pytest configuration and fixtures for backend tests."""

import logging
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest

# Silence httpx INFO logs during tests
logging.getLogger("httpx").setLevel(logging.WARNING)

# Enable pytest-databases PostgreSQL plugin for CI/CD
pytest_plugins = ["pytest_databases.docker.postgres"]

# Import and discover all models before tests run
from app.utils.discovery import discover_and_import

discover_and_import(["models.py", "models/**/*.py"], base_path="app")

from litestar import Litestar
from litestar.di import Provide
from litestar.middleware.session.server_side import ServerSideSessionConfig
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
from app.factory import create_app
from app.media.routes import media_router
from app.objects.routes import object_router
from app.payments.routes import invoice_router
from app.roster.routes import roster_router
from app.teams.routes import team_router
from app.threads import thread_router
from app.threads.websocket import thread_handler
from app.users.routes import user_router
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
def test_db_url(postgres_service) -> str:
    """Test database URL using pytest-databases PostgreSQL service.

    This works in both local development and CI/CD environments.
    The postgres_service fixture is provided by pytest-databases and automatically
    starts a Docker container with PostgreSQL.
    """
    return (
        f"postgresql+psycopg://{postgres_service.user}:{postgres_service.password}@"
        f"{postgres_service.host}:{postgres_service.port}/{postgres_service.database}"
    )


@pytest.fixture(scope="session")
def test_engine(test_db_url: str):
    """Create a test database engine for the entire test session."""
    engine = create_async_engine(
        test_db_url,
        echo=False,
        poolclass=NullPool,  # Don't use StaticPool with Docker postgres
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
            # Drop all tables with CASCADE to handle foreign key constraints
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        await test_engine.dispose()

    # Run setup
    asyncio.run(_setup())

    yield

    # Run teardown
    asyncio.run(_teardown())


@pytest.fixture
async def db_session(test_engine, setup_database) -> AsyncGenerator[AsyncSession]:
    """Provide a clean database session for each test with automatic rollback.

    Each test gets an isolated transaction that is rolled back after the test,
    ensuring no test pollution.
    """
    from sqlalchemy.orm import raiseload

    def _raiseload_listener(execute_state):
        """Prevent lazy loading by raising an error when relationships are accessed without explicit loading."""
        execute_state.statement = execute_state.statement.options(raiseload("*"))

    session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autobegin=True,
    )

    session = session_maker()
    try:
        # Attach listeners for soft delete filter and raiseload
        event.listen(session.sync_session, "do_orm_execute", apply_soft_delete_filter)
        event.listen(session.sync_session, "do_orm_execute", _raiseload_listener)

        yield session
    finally:
        # Remove listeners
        event.remove(session.sync_session, "do_orm_execute", apply_soft_delete_filter)
        event.remove(session.sync_session, "do_orm_execute", _raiseload_listener)

        # Rollback any pending transaction
        await session.rollback()

        # Explicitly close session to release connection back to pool
        await session.close()


# ============================================================================
# Test Configuration & Dependencies
# ============================================================================


@pytest.fixture
def test_config(test_db_url: str, monkeypatch) -> Config:
    """Provide test configuration with safe defaults."""

    # Set environment variables before creating Config instance
    # Config.DATABASE_URL reads from os.getenv("DATABASE_URL")
    monkeypatch.setenv("ENV", "testing")
    monkeypatch.setenv("DATABASE_URL", test_db_url.replace("postgresql+psycopg://", "postgresql://"))
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("SESSION_COOKIE_DOMAIN", "localhost")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:3000")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")

    # Create config after environment variables are set
    config = Config()
    return config


@pytest.fixture
def mock_s3_client():
    """Provide a mocked S3 client for testing."""
    from pathlib import Path

    from app.client.s3_client import BaseS3Client

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
def test_app(
    test_config: Config,
    db_session: AsyncSession,
    mock_s3_client: Any,
    mock_http_client: Any,
) -> Litestar:
    """Create a Litestar app configured for testing.

    The factory has production defaults. We override:
    - Dependencies: transaction, http_client, s3_client (mocks)
    - Plugins: StaticPool for DB, SAQ with in-memory queue, memory channels
    - Stores: MemoryStore for sessions

    SAQ tasks run synchronously and immediately during tests.
    """
    from litestar.channels import ChannelsPlugin
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.plugins.sqlalchemy import (
        AsyncSessionConfig,
        EngineConfig,
        SQLAlchemyAsyncConfig,
        SQLAlchemyPlugin,
    )

    from app.base.models import BaseDBModel

    # Create provider functions that close over test fixtures
    def provide_test_transaction() -> AsyncSession:
        return db_session

    def provide_test_http_client() -> Any:
        return mock_http_client

    def provide_test_s3_client() -> Any:
        return mock_s3_client

    def provide_test_task_queues() -> Any:
        """Provide a TaskQueues object for testing."""
        # Import the real TaskQueues class and create an empty instance
        # This satisfies Litestar's type checking without needing actual queues
        from litestar_saq import TaskQueues

        # Create empty TaskQueues dict - tests don't actually enqueue tasks
        return TaskQueues({})

    # Create app with test-specific overrides
    app = create_app(
        config=test_config,
        # Override external service dependencies for testing
        dependencies_overrides={
            "transaction": Provide(provide_test_transaction, sync_to_thread=False),
            "http_client": Provide(provide_test_http_client, sync_to_thread=False),
            "s3_client": Provide(provide_test_s3_client, sync_to_thread=False),
            "task_queues": Provide(provide_test_task_queues, sync_to_thread=False),
        },
        # Override plugins for testing: StaticPool DB, memory channels, no SAQ
        plugins_overrides=[
            SQLAlchemyPlugin(
                config=SQLAlchemyAsyncConfig(
                    connection_string=test_config.ASYNC_DATABASE_URL,
                    metadata=BaseDBModel.metadata,
                    engine_config=EngineConfig(
                        poolclass=StaticPool,
                        connect_args={},
                        pool_pre_ping=False,
                    ),
                    session_config=AsyncSessionConfig(
                        expire_on_commit=False,
                        autoflush=False,
                        autobegin=True,
                    ),
                    create_all=False,
                )
            ),
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

    async with AsyncTestClient(app=test_app, session_config=session_config) as client:
        yield client


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
async def authenticated_client(
    test_client: AsyncTestClient[Litestar],
    db_session: AsyncSession,
) -> AsyncGenerator[tuple[AsyncTestClient[Litestar], dict[str, Any]]]:
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
    from app.users.models import Role
    from tests.factories.users import TeamFactory, UserFactory

    # Create test user and team
    team = await TeamFactory.create_async(session=db_session)
    user = await UserFactory.create_async(
        session=db_session,
    )

    # Create role to link user to team
    role = Role(user_id=user.id, team_id=team.id, role_level="member")
    db_session.add(role)

    await db_session.commit()

    # Set session data to authenticate
    await test_client.set_session_data(
        {
            "user_id": int(user.id),  # Convert Sqid to int for session storage
            "team_id": int(team.id),  # Convert Sqid to int for session storage
            "scope_type": ScopeType.TEAM.value,
        }
    )

    user_data = {
        "user_id": int(user.id),  # Convert Sqid to int for route parameters
        "team_id": int(team.id),  # Convert Sqid to int for route parameters
        "email": user.email,
        "team": team,
        "user": user,
    }

    yield test_client, user_data


@pytest.fixture
async def other_team_client(
    test_client: AsyncTestClient[Litestar],
    db_session: AsyncSession,
) -> AsyncGenerator[tuple[AsyncTestClient[Litestar], dict[str, Any]]]:
    """Provide an authenticated test client for a different team (for RLS isolation tests).

    This fixture uses a separate test client instance to simulate a different user/team
    accessing the same resources.

    Returns:
        Tuple of (client, user_data) where user_data contains user_id, team_id, etc.

    Usage:
        async def test_rls_isolation(authenticated_client, other_team_client):
            client, user_data = authenticated_client
            other_client, other_user_data = other_team_client
            # Test that other_client cannot access user_data's resources
    """
    # Import factories here to avoid circular imports
    from app.users.models import Role
    from tests.factories.users import TeamFactory, UserFactory

    # Create a separate user and team
    other_team = await TeamFactory.create_async(session=db_session)
    other_user = await UserFactory.create_async(
        session=db_session,
    )

    # Create role to link user to team
    role = Role(user_id=other_user.id, team_id=other_team.id, role_level="member")
    db_session.add(role)

    await db_session.commit()

    # Set session data for the other team (reusing the same client but different session)
    # Note: This simulates a different authenticated user making requests
    await test_client.set_session_data(
        {
            "user_id": int(other_user.id),
            "team_id": int(other_team.id),
            "scope_type": ScopeType.TEAM.value,
        }
    )

    other_user_data = {
        "user_id": int(other_user.id),
        "team_id": int(other_team.id),
        "email": other_user.email,
        "team": other_team,
        "user": other_user,
    }

    yield test_client, other_user_data

    # Note: The authenticated_client fixture will reset the session after this test


@pytest.fixture
async def admin_client(
    test_client: AsyncTestClient[Litestar],
    db_session: AsyncSession,
) -> AsyncGenerator[tuple[AsyncTestClient[Litestar], dict[str, Any]]]:
    """Provide an authenticated admin client for testing admin endpoints."""
    from app.users.models import Role
    from tests.factories.users import TeamFactory, UserFactory

    team = await TeamFactory.create_async(session=db_session)
    admin = await UserFactory.create_async(
        session=db_session,
    )

    # Create admin role to link user to team
    role = Role(user_id=admin.id, team_id=team.id, role_level="admin")
    db_session.add(role)

    await db_session.commit()

    await test_client.set_session_data(
        {
            "user_id": int(admin.id),  # Convert Sqid to int for session storage
            "team_id": int(team.id),  # Convert Sqid to int for session storage
            "scope_type": ScopeType.TEAM.value,
        }
    )

    admin_data = {
        "user_id": int(admin.id),  # Convert Sqid to int for route parameters
        "team_id": int(team.id),  # Convert Sqid to int for route parameters
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
    from app.users.models import Role
    from tests.factories.users import TeamFactory, UserFactory

    team1 = await TeamFactory.create_async(session=db_session, name="Team 1")
    team2 = await TeamFactory.create_async(session=db_session, name="Team 2")

    user1 = await UserFactory.create_async(
        session=db_session,
        email="user1@team1.com",
    )
    user2 = await UserFactory.create_async(
        session=db_session,
        email="user2@team2.com",
    )

    # Create roles to link users to teams
    role1 = Role(user_id=user1.id, team_id=team1.id, role_level="member")
    role2 = Role(user_id=user2.id, team_id=team2.id, role_level="member")
    db_session.add(role1)
    db_session.add(role2)

    await db_session.commit()

    return {
        "team1": team1,
        "team2": team2,
        "user1": user1,
        "user2": user2,
    }


# ============================================================================
# Factory Helper Fixtures
# ============================================================================


@pytest.fixture
def create_complete_campaign(db_session: AsyncSession):
    """Factory helper to create a campaign with all dependencies.

    Creates: Brand, Roster, Campaign, and optionally Contract.

    Usage:
        async def test_example(create_complete_campaign):
            campaign, brand, roster, contract = await create_complete_campaign(
                add_contract=True
            )
    """

    async def _create(
        add_contract: bool = False,
        campaign_kwargs: dict[str, Any] | None = None,
        brand_kwargs: dict[str, Any] | None = None,
        roster_kwargs: dict[str, Any] | None = None,
        contract_kwargs: dict[str, Any] | None = None,
    ):
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory
        from tests.factories.users import RosterFactory

        brand = await BrandFactory.create_async(session=db_session, **(brand_kwargs or {}))
        roster = await RosterFactory.create_async(session=db_session, **(roster_kwargs or {}))
        campaign = await CampaignFactory.create_async(session=db_session, brand_id=brand.id, **(campaign_kwargs or {}))

        # Note: ContractFactory doesn't exist yet - contracts feature not implemented
        contract = None
        # if add_contract:
        #     contract = await ContractFactory.create_async(
        #         session=db_session,
        #         campaign_id=campaign.id,
        #         roster_id=roster.id,
        #         **(contract_kwargs or {}),
        #     )

        await db_session.commit()
        return campaign, brand, roster, contract

    return _create


@pytest.fixture
def create_brand_with_contacts(db_session: AsyncSession):
    """Factory helper to create a brand with multiple contacts.

    Usage:
        async def test_example(create_brand_with_contacts):
            brand, contacts = await create_brand_with_contacts(num_contacts=3)
    """

    async def _create(
        num_contacts: int = 2,
        brand_kwargs: dict[str, Any] | None = None,
        contact_kwargs: dict[str, Any] | None = None,
    ):
        from tests.factories.brands import BrandContactFactory, BrandFactory

        brand = await BrandFactory.create_async(session=db_session, **(brand_kwargs or {}))

        contacts = []
        for i in range(num_contacts):
            contact = await BrandContactFactory.create_async(
                session=db_session,
                brand_id=brand.id,
                name=f"Contact {i + 1}",
                email=f"contact{i + 1}@example.com",
                **(contact_kwargs or {}),
            )
            contacts.append(contact)

        await db_session.commit()
        return brand, contacts

    return _create


@pytest.fixture
def create_deliverable_with_media(db_session: AsyncSession):
    """Factory helper to create a deliverable with media associations.

    Usage:
        async def test_example(create_deliverable_with_media):
            deliverable, campaign, media_list = await create_deliverable_with_media(
                num_media=2
            )
    """

    async def _create(
        num_media: int = 1,
        deliverable_kwargs: dict[str, Any] | None = None,
        campaign_kwargs: dict[str, Any] | None = None,
        media_kwargs: dict[str, Any] | None = None,
    ):
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory
        from tests.factories.deliverables import DeliverableFactory
        from tests.factories.media import MediaFactory

        # Create campaign with brand
        brand = await BrandFactory.create_async(session=db_session)
        campaign = await CampaignFactory.create_async(session=db_session, brand_id=brand.id, **(campaign_kwargs or {}))

        # Create deliverable
        deliverable = await DeliverableFactory.create_async(
            session=db_session, campaign_id=campaign.id, **(deliverable_kwargs or {})
        )

        # Create media and associations
        media_list = []
        for i in range(num_media):
            media = await MediaFactory.create_async(session=db_session, **(media_kwargs or {}))
            # Note: DeliverableMediaFactory doesn't exist yet - many-to-many not implemented
            # await DeliverableMediaFactory.create_async(
            #     session=db_session,
            #     deliverable_id=deliverable.id,
            #     media_id=media.id,
            # )
            media_list.append(media)

        await db_session.commit()
        return deliverable, campaign, media_list

    return _create


# ============================================================================
# Common Object Fixtures for Tests
# ============================================================================


@pytest.fixture
async def user(
    authenticated_client: tuple[AsyncTestClient, dict],
):
    """Get the user from the authenticated client.

    Returns:
        User instance
    """
    client, user_data = authenticated_client
    return user_data["user"]


@pytest.fixture
async def team(
    authenticated_client: tuple[AsyncTestClient, dict],
):
    """Get the team from the authenticated client.

    Returns:
        Team instance
    """
    client, user_data = authenticated_client
    return user_data["team"]


@pytest.fixture
async def brand(
    team,
    db_session: AsyncSession,
):
    """Create a brand associated with the given team.

    Returns:
        Brand instance
    """
    from tests.factories.brands import BrandFactory

    brand = await BrandFactory.create_async(
        session=db_session,
        team_id=team.id,
    )
    await db_session.commit()
    return brand


@pytest.fixture
async def campaign(
    team,
    brand,
    db_session: AsyncSession,
):
    """Create a campaign with a brand, associated with the given team.

    Returns:
        Campaign instance
    """
    from tests.factories.campaigns import CampaignFactory

    campaign = await CampaignFactory.create_async(
        session=db_session,
        team_id=team.id,
        brand_id=brand.id,
    )
    await db_session.commit()
    return campaign


@pytest.fixture
async def roster(
    team,
    user,
    db_session: AsyncSession,
):
    """Create a roster member associated with the given team.

    Returns:
        Roster instance
    """
    from tests.factories.users import RosterFactory

    roster = await RosterFactory.create_async(
        session=db_session,
        team_id=team.id,
        user_id=user.id,
        profile_photo_id=None,  # Don't create a profile photo by default
    )
    await db_session.commit()
    return roster


@pytest.fixture
async def deliverable(
    team,
    campaign,
    db_session: AsyncSession,
):
    """Create a deliverable associated with the given campaign.

    Returns:
        Deliverable instance
    """
    from tests.factories.deliverables import DeliverableFactory

    deliverable = await DeliverableFactory.create_async(
        session=db_session,
        team_id=team.id,
        campaign_id=campaign.id,
    )
    await db_session.commit()
    return deliverable


@pytest.fixture
async def document(
    team,
    db_session: AsyncSession,
):
    """Create a document associated with the given team.

    Returns:
        Document instance
    """
    from tests.factories.documents import DocumentFactory

    document = await DocumentFactory.create_async(
        session=db_session,
        team_id=team.id,
    )
    await db_session.commit()
    return document


@pytest.fixture
async def invoice(
    team,
    db_session: AsyncSession,
):
    """Create an invoice associated with the given team.

    Returns:
        Invoice instance
    """
    from tests.factories.payments import InvoiceFactory

    invoice = await InvoiceFactory.create_async(
        session=db_session,
        team_id=team.id,
    )
    await db_session.commit()
    return invoice
