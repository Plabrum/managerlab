# Backend Testing Setup - Comprehensive Analysis

## Executive Summary

The managerlab backend has a **minimal but well-structured testing foundation** using pytest with async support. Currently only 4 test files exist with basic unit tests. The project has extensive testing infrastructure in place (factories, fixtures, conftest) but lacks comprehensive endpoint integration tests.

---

## Current Test Files & Coverage

### Test Files Location
- **Path:** `/backend/tests/`
- **Root test:** `/backend/test_factory.py` (discovery script, not a test)

### Existing Tests (4 files)

#### 1. **test_basic.py**
- **Type:** Unit tests (sanity checks)
- **Coverage:** Basic Python functionality
- **Tests:**
  - `test_basic_functionality()` - Simple math assertion
  - `test_string_operations()` - String concatenation
  - `test_list_operations()` - List operations
  - `test_square_function()` - Parametrized test example
- **Status:** Passes ✓
- **Purpose:** Verifies pytest is working in CI

#### 2. **test_event_consumers.py**
- **Type:** Unit tests (business logic)
- **Coverage:** Event consumer helper functions
- **Tests:** 16 comprehensive tests covering:
  - `TestParseEventDataToUpdated` - Parsing event data to UpdatedEventData schema
  - `TestBuildUpdateMessageContent` - Building TipTap formatted messages
  - `TestIntegration` - Full workflow tests
- **Key Functions Tested:**
  - `_parse_event_data_to_updated()` - Converts raw event data to structured format
  - `build_update_message_content()` - Generates TipTap content nodes for activity messages
- **Status:** Passes ✓
- **Notes:** Tests edge cases like None values, invalid fields, underscore conversions

#### 3. **test_thread_viewer_store.py**
- **Type:** Async unit tests
- **Coverage:** ThreadViewerStore in-memory cache service
- **Tests:** 3 async test methods covering:
  - `test_add_and_remove_viewers_workflow()` - Full workflow of viewer management
  - `test_edge_cases_and_graceful_handling()` - Removing non-existent viewers
  - `test_simultaneous_threads()` - Multiple thread independence
- **Dependencies:** Uses `memory_store` fixture from conftest
- **Status:** Passes ✓
- **Notes:** Uses pytest-asyncio for async testing

#### 4. **test_factory.py** (Root directory)
- **Type:** Discovery/exploration script (not a formal test)
- **Purpose:** Understanding polyfactory API
- **Content:** Test factories for Brand and BrandContact models
- **Note:** Should be moved to `/tests/factories/` or converted to proper test

### Test Coverage Assessment

| Area | Coverage | Status |
|------|----------|--------|
| **API Endpoints** | 0% | MISSING |
| **Route Handlers** | 0% | MISSING |
| **Business Logic** | ~5% | PARTIAL (event consumers, thread viewer store) |
| **Database Models** | 0% | MISSING |
| **Authentication** | 0% | MISSING |
| **Authorization** | 0% | MISSING |
| **Error Handling** | ~20% | PARTIAL (edge cases in existing tests) |

---

## Testing Infrastructure

### Pytest Configuration

**File:** `/backend/pyproject.toml`

```toml
[tool.pytest]
# Not explicitly configured, uses defaults
```

**Key Dependencies:**
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `polyfactory>=2.22.2` - Data factory generation
- `faker>=37.6.0` - Fake data generation

**Run Command:**
```bash
make test  # Runs pytest with backend tests
```

### Fixtures & Setup

**File:** `/backend/tests/conftest.py`

```python
@pytest.fixture
def memory_store() -> MemoryStore:
    """Provide a fresh MemoryStore instance for each test."""
    return MemoryStore()
```

**Current Fixtures:**
- `memory_store` - MemoryStore instance for caching tests

**Missing Fixtures:**
- Database session/transaction fixture
- Authenticated request fixture
- User/Team/Campaign factory instances
- HTTP client for endpoint testing
- Dependency injection setup for route handlers

---

## Model Factories

**Location:** `/backend/tests/factories/`

### Available Factory Files

#### 1. **base.py**
```python
class BaseFactory(SQLAlchemyFactory[BaseDBModel]):
    """Base factory for all database models."""
    __faker__ = Faker()
    __session__ = None  # Set at runtime
    __check_model__ = False
    __set_relationships__ = False
    __set_association_proxy__ = False
```

**Configuration:**
- Uses polyfactory's SQLAlchemyFactory
- Disables relationship auto-population (clean data)
- No association proxy handling (to avoid complexity)

#### 2. **users.py**
```python
class UserFactory(BaseFactory):
    name = Use(BaseFactory.__faker__.name)
    email = Use(BaseFactory.__faker__.email)
    email_verified = Use(BaseFactory.__faker__.boolean, chance_of_getting_true=80)
    state = UserStates.ACTIVE

class TeamFactory(BaseFactory):
    name = Use(BaseFactory.__faker__.company)
    description = Use(BaseFactory.__faker__.catch_phrase)

class RoleFactory(BaseFactory):
    role_level = RoleLevel.MEMBER

class RosterFactory(BaseFactory):
    name = Use(BaseFactory.__faker__.name)
    email = Use(BaseFactory.__faker__.email)
    # ... other fields

class WaitlistEntryFactory(BaseFactory):
    # ... user signup data
```

#### 3. **brands.py**
- BrandFactory
- BrandContactFactory

#### 4. **campaigns.py**
- CampaignFactory
- ContractFactory (likely)

#### 5. **deliverables.py**
- DeliverableFactory

#### 6. **media.py**
- MediaFactory

#### 7. **payments.py**
- InvoiceFactory
- PaymentFactory (likely)

#### 8. **auth.py**
- OAuth-related factories

---

## API Routes & Endpoints

### All Available Routes (12 routers)

#### 1. **Auth Routes** (`/auth`)
- **File:** `/backend/app/auth/routes.py`
- **Endpoints:**
  - `GET /auth/list-scopes` - List user's available teams and campaigns
  - `POST /auth/switch-scope` - Switch between team/campaign scope
  - `POST /auth/logout` - Clear session
  - Includes Google OAuth router (`/auth/google/`)
- **Guards:** Requires authenticated user (except logout)

#### 2. **Users Routes** (`/users`)
- **File:** `/backend/app/users/routes.py`
- **Public Endpoints:**
  - `POST /users/signup` - Add user to waitlist (no auth required)
- **Authenticated Endpoints:**
  - `GET /users/` - List all users (superuser only)
  - `GET /users/{user_id}` - Get user by ID
  - `POST /users/` - Create new user (superuser only)
  - `GET /users/current_user` - Get current authenticated user
  - `POST /users/teams` - Create new team
  - `GET /users/teams` - List user's teams
  - `POST /users/switch-team` - Switch active team
- **Guards:** Most require `requires_user_id` (authenticated)

#### 3. **Brands Routes** (`/brands`)
- **File:** `/backend/app/brands/routes.py`
- **Endpoints:**
  - `GET /brands/{id}` - Get brand (with thread info, actions)
  - `POST /brands/{id}` - Update brand
  - `GET /brands/contacts/{id}` - Get brand contact
  - `POST /brands/contacts/{id}` - Update brand contact
- **Guards:** All require `requires_user_id`
- **Features:** Thread integration, action registry, SQID encoding

#### 4. **Campaigns Routes** (`/campaigns`)
- **File:** `/backend/app/campaigns/routes.py`
- **Endpoints:**
  - `GET /campaigns/{id}` - Get campaign (extensive schema)
  - `POST /campaigns/{id}` - Update campaign
- **Guards:** Requires `requires_user_id`
- **Features:** Complex schema with contract, flight dates, exclusivity, approval settings

#### 5. **Objects Routes** (`/objects`)
- **File:** `/backend/app/objects/routes.py`
- **Type:** Generic object CRUD operations
- **Guards:** Requires `requires_user_id`

#### 6. **Actions Routes** (`/actions`)
- **File:** `/backend/app/actions/routes.py`
- **Type:** Action registry and execution
- **Guards:** Requires `requires_user_id`

#### 7. **Roster Routes** (`/roster`)
- **File:** `/backend/app/roster/routes.py`
- **Type:** Influencer/team member roster management

#### 8. **Deliverables Routes** (`/deliverables`)
- **File:** `/backend/app/deliverables/routes.py`
- **Type:** Project deliverables management

#### 9. **Threads Routes** (`/threads`)
- **File:** `/backend/app/threads/routes.py`
- **Endpoints:**
  - `POST /threads/{threadable_type}/{threadable_id}/messages` - Create message
  - Thread WebSocket handler (separate)
- **Features:** Real-time messaging via WebSocket with Channels plugin
- **Dependencies:** AsyncSession, ChannelsPlugin, ThreadViewerStore

#### 10. **Documents Routes** (`/documents`)
- **File:** `/backend/app/documents/routes/documents.py`
- **Type:** Document management and upload

#### 11. **Media Routes** (`/media`)
- **Files:**
  - `local_media_router` - Local file uploads (dev only)
  - `media_router` - S3-based media management
- **Features:** S3 integration, S3 client provider

#### 12. **Payments/Invoices Routes** (`/payments`)
- **File:** `/backend/app/payments/routes.py`
- **Type:** Invoice and payment management

#### 13. **Dashboard Routes** (`/dashboard`)
- **File:** `/backend/app/dashboard/routes.py`
- **Type:** Dashboard data aggregation

#### 14. **System Routes**
- `GET /health` - Health check (no auth required)

### Route Patterns & Common Features

**Authentication Guards:**
```python
@requires_user_id       # Basic authentication
@requires_superuser     # Admin-only
@requires_user_scope    # Team/campaign scope validation
```

**Dependency Injection:**
All routes receive these injected dependencies:
- `request: Request` - HTTP request context
- `transaction: AsyncSession` - Database session
- `action_registry: ActionRegistry` - Available actions
- `team_id: int | None` - Current team (from session)
- `campaign_id: int | None` - Current campaign (from session)
- `channels: ChannelsPlugin` - WebSocket channels (threads only)

**SQID Encoding:**
- Routes use `Sqid` type for IDs instead of raw integers
- Example: `GET /brands/{id:str}` where id is a Sqid
- Transparent encoding/decoding via type hooks

---

## Dependency Injection System

**File:** `/backend/app/utils/providers.py`

### Provided Dependencies

```python
def provide_transaction(db_session: AsyncSession, request: Request) -> AsyncGenerator[AsyncSession]
def provide_team_id(request: Request) -> int | None
def provide_campaign_id(request: Request) -> int | None
def provide_viewer_store(request: Request) -> ThreadViewerStore
def provide_action_registry(...) -> ActionRegistry
def provide_object_registry(...) -> ObjectRegistry
def provide_http(...) -> aiohttp.ClientSession
```

### Key Features

- **RLS Variables:** Sets Row-Level Security variables for data filtering
- **Soft Delete Filter:** Automatically filters deleted records
- **Raiseload Listener:** Prevents lazy-loading within transactions
- **IntegrityError Handling:** Converts DB errors to HTTP 409 Conflict

---

## Database & Models

### Base Model Structure
**File:** `/backend/app/base/models.py`

Key features:
- SQLAlchemy 2.0 async-first
- Soft delete support via `deleted_at` timestamp
- RLS (Row-Level Security) integration
- Automatic timestamp tracking (`created_at`, `updated_at`)
- SQID encoding/decoding support

### Main Domain Models

```
Users:           User, Team, Role, WaitlistEntry
Brands:          Brand, BrandContact
Campaigns:       Campaign, CampaignGuest, Contract
Roster:          Roster (influencers/team members)
Threads:         Thread, Message, ReadStatus
Deliverables:    Deliverable
Media:           MediaFile
Documents:       Document
Payments:        Invoice, Payment
State Machine:   StateMachine (workflow)
Events:          Event, ActivityLog
```

---

## Testing Patterns & Best Practices

### Current Patterns

#### 1. **Async Test Pattern** (from test_thread_viewer_store.py)
```python
@pytest.mark.asyncio
async def test_add_and_remove_viewers_workflow(self, memory_store: MemoryStore) -> None:
    store = ThreadViewerStore(store=memory_store)
    # Test async operations
    await store.add_viewer(thread_id, 101)
```

#### 2. **Parametrized Tests** (from test_basic.py)
```python
@pytest.mark.parametrize("input_val,expected", [(2, 4), (3, 9)])
def test_square_function(input_val, expected):
    assert square(input_val) == expected
```

#### 3. **Mock Objects** (from test_event_consumers.py)
```python
class MockObject:
    def __init__(self, id: int, name: str | None = None):
        self.id = id
        self.name = name
```

---

## Recommended Approach for Comprehensive Endpoint Testing

### Phase 1: Foundation Setup (Priority: Critical)

#### 1.1 Create Database Fixtures
```python
# tests/fixtures/database.py
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Provide isolated database session for each test."""
    # Create test database URL
    # Setup async engine
    # Begin transaction
    # Yield session
    # Rollback (no test data persists)
```

#### 1.2 Create Authentication Fixtures
```python
@pytest.fixture
def authenticated_request(user: User) -> Request:
    """Create mock request with authenticated user."""
    # Set request.user = user.id
    # Set request.session with team/campaign scope
    # Return mocked Request object
```

#### 1.3 Create Factory Fixtures
```python
@pytest.fixture
def user_factory(db_session: AsyncSession):
    UserFactory.__session__ = db_session
    return UserFactory

@pytest.fixture
async def user(user_factory) -> User:
    return await user_factory.create()

@pytest.fixture
async def team(team_factory: TeamFactory, user: User) -> Team:
    team = await team_factory.create()
    # Link user to team via Role
    return team
```

#### 1.4 Create HTTP Client Fixture
```python
@pytest.fixture
async def client(app: Litestar) -> AsyncClient:
    """Create authenticated test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Set session cookies for auth
        yield ac
```

### Phase 2: Route Testing Framework

#### 2.1 Create Test Base Classes
```python
# tests/base.py
class APITestCase:
    """Base class for endpoint tests."""
    
    async def test_requires_authentication(self):
        """Standard test: verify endpoint requires auth."""
    
    async def test_requires_team_scope(self):
        """Standard test: verify endpoint requires team scope."""
    
    async def test_404_not_found(self):
        """Standard test: verify 404 handling."""
```

#### 2.2 Organize Tests by Feature
```
tests/
├── fixtures/
│   ├── __init__.py
│   ├── database.py       # DB sessions
│   ├── auth.py           # Auth fixtures
│   └── factories.py      # Factory fixtures
├── routes/               # Route/endpoint tests
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_brands.py
│   ├── test_campaigns.py
│   ├── test_threads.py
│   └── ...
├── schemas/              # Schema validation tests
├── models/               # Model relationship tests
└── integration/          # Multi-endpoint workflows
```

### Phase 3: Specific Test Patterns

#### 3.1 Endpoint Test Template
```python
# tests/routes/test_users.py
import pytest
from httpx import AsyncClient

class TestGetCurrentUser:
    """Test GET /users/current_user endpoint."""
    
    async def test_returns_current_user_when_authenticated(
        self, 
        client: AsyncClient, 
        authenticated_user: User
    ):
        """Verify endpoint returns current user when authenticated."""
        response = await client.get("/users/current_user")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == authenticated_user.id
        assert data["email"] == authenticated_user.email
    
    async def test_returns_401_when_not_authenticated(self, client: AsyncClient):
        """Verify endpoint requires authentication."""
        response = await client.get("/users/current_user")
        assert response.status_code == 401
```

#### 3.2 CRUD Test Pattern
```python
class TestBrandAPI:
    """Test Brand endpoints (GET, POST)."""
    
    async def test_get_brand(self, client, brand: Brand):
        response = await client.get(f"/brands/{sqid_encode(brand.id)}")
        assert response.status_code == 200
        assert response.json()["name"] == brand.name
    
    async def test_update_brand(self, client, brand: Brand):
        response = await client.post(
            f"/brands/{sqid_encode(brand.id)}",
            json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
    
    async def test_get_nonexistent_brand_returns_404(self, client):
        response = await client.get("/brands/9999999")
        assert response.status_code == 404
```

#### 3.3 Authorization Test Pattern
```python
class TestBrandAuthorization:
    """Test Brand endpoint authorization."""
    
    async def test_user_cannot_access_other_team_brand(
        self, 
        client: AsyncClient,
        other_team_brand: Brand
    ):
        """Verify RLS prevents cross-team access."""
        response = await client.get(f"/brands/{sqid_encode(other_team_brand.id)}")
        assert response.status_code == 404  # RLS hides it
```

### Phase 4: Coverage Goals

**Priority Order:**
1. Authentication routes (`/auth/*`) - Critical for app flow
2. User routes (`/users/*`) - Core functionality
3. Team/Campaign scope switching - Required for multi-tenant isolation
4. Brand/Campaign CRUD - Main business entities
5. Thread messaging - Real-time feature
6. Everything else

**Initial Target:**
- All public/auth endpoints: 90%+ coverage
- Core CRUD operations: 85%+ coverage
- Error cases: 70%+ coverage
- Advanced features: 50%+ coverage

---

## Testing Infrastructure Summary

### Tools & Libraries

| Component | Tool | Status |
|-----------|------|--------|
| **Test Runner** | pytest | ✓ Installed |
| **Async Support** | pytest-asyncio | ✓ Installed |
| **Data Factory** | polyfactory | ✓ Installed |
| **Fake Data** | faker | ✓ Installed |
| **HTTP Client** | httpx | NEEDED |
| **Database** | PostgreSQL | ✓ Available |
| **ORM** | SQLAlchemy 2.0 | ✓ Installed |
| **Test DB** | Docker compose | ✓ Available |

### Missing but Recommended Tools

```toml
# Add to pyproject.toml [dev dependencies]
"httpx>=0.25.0",           # Async HTTP client for testing
"pytest-cov>=4.1.0",       # Coverage reporting
"pytest-mock>=3.12.0",     # Mocking utilities
"pytest-timeout>=2.2.0",   # Test timeout protection
"factory-boy>=3.3.0",      # Alternative factory pattern (optional)
```

---

## Configuration Files Summary

### Makefile Commands
```bash
make test              # Run pytest tests
make check-backend     # Run type checking + tests
make db-start          # Start PostgreSQL (needed for integration tests)
make db-migrate        # Create migrations
make db-upgrade        # Apply migrations
```

### pytest.ini / pyproject.toml
- **Location:** `/backend/pyproject.toml`
- **Current:** Minimal configuration
- **Recommended additions:**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_scope = "function"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --tb=short"
markers = [
    "asyncio: async tests",
    "integration: integration tests",
    "slow: slow tests",
    "unit: unit tests",
]
```

---

## Quick Start for Writing Tests

### Example: Testing a Simple Endpoint

```python
# tests/routes/test_brands.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.brands.models import Brand
from tests.factories.brands import BrandFactory

class TestGetBrand:
    @pytest.mark.asyncio
    async def test_get_brand_success(
        self,
        db_session: AsyncSession,
        authenticated_client,
        user_team: tuple
    ):
        """Test successfully getting a brand."""
        user, team = user_team
        
        # Create brand
        brand = await BrandFactory.create(
            session=db_session,
            team_id=team.id,
            name="Test Brand"
        )
        await db_session.flush()
        
        # Make request
        response = await authenticated_client.get(f"/brands/{brand.id}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["name"] == "Test Brand"
```

---

## Current Gaps & Action Items

### Critical Gaps
- [ ] No integration tests for API endpoints
- [ ] No database fixtures for isolated test data
- [ ] No authenticated request fixtures
- [ ] No HTTP client setup for testing routes
- [ ] No tests for authentication/authorization
- [ ] No tests for real-time WebSocket functionality
- [ ] No tests for error handling/edge cases in routes
- [ ] No tests for RLS (Row-Level Security) isolation

### Important Missing Areas
- [ ] Schema validation tests
- [ ] Model relationship tests
- [ ] Action registry tests
- [ ] Object registry tests
- [ ] Queue/task tests
- [ ] Session management tests
- [ ] SQID encoding/decoding tests

### Nice-to-Have
- [ ] Performance benchmarks
- [ ] Load testing setup
- [ ] Contract testing (for API consumers)
- [ ] Mutation testing
- [ ] Coverage reporting in CI

---

## Next Steps Recommendation

1. **Week 1:** Set up database and auth fixtures (foundation)
2. **Week 2:** Create test templates and test 2-3 simple endpoints
3. **Week 3:** Expand to all CRUD endpoints (brands, campaigns, etc.)
4. **Week 4:** Add authorization/error case testing
5. **Ongoing:** Maintain 80%+ coverage for new code

This structured approach will provide comprehensive endpoint coverage while building a maintainable testing framework.
