# Backend Testing - Quick Reference

## Current Testing Status

```
Total Test Files: 4
├── test_basic.py                    [4 tests]  ✓ Passing
├── test_event_consumers.py         [16 tests] ✓ Passing
├── test_thread_viewer_store.py      [3 tests] ✓ Passing
└── test_factory.py                  [discovery script - not a test]

Total API Endpoints: ~40 endpoints across 13 routers
Total Route Tests: 0
Test Coverage: ~5% (mostly utilities, no endpoints)
```

## API Endpoints by Module

```
/health                           [GET]  ✓ No auth
/auth                            [POST] Multiple endpoints
├── /auth/list-scopes            [GET]
├── /auth/switch-scope           [POST]
├── /auth/logout                 [POST]
└── /auth/google/...             [Google OAuth]

/users                           [Multiple endpoints]
├── /users/signup               [POST]  No auth
├── /users/current_user         [GET]
├── /users/{id}                 [GET]
├── /users/teams                [GET/POST]
└── /users/switch-team          [POST]

/brands                          [GET/POST per item]
├── /brands/{id}                [GET/POST]
└── /brands/contacts/{id}       [GET/POST]

/campaigns                       [GET/POST per item]
└── /campaigns/{id}             [GET/POST]

/threads
├── /threads/{type}/{id}/messages [POST]
└── /threads/{type}/{id}         [WebSocket]

/roster                          [CRUD]
/deliverables                    [CRUD]
/documents                       [CRUD]
/media                           [CRUD + S3]
/payments                        [CRUD]
/objects                         [Generic CRUD]
/actions                         [Registry]
/dashboard                       [Aggregation]
```

## Testing Stack

### Installed
- ✓ pytest
- ✓ pytest-asyncio
- ✓ polyfactory
- ✓ faker
- ✓ SQLAlchemy 2.0 async
- ✓ PostgreSQL

### Missing (Needed for endpoint tests)
- httpx (async HTTP client)
- pytest-cov (coverage reporting)
- pytest-mock (mocking)

## Factory Files Available

```
tests/factories/
├── base.py              BaseFactory (SQLAlchemy)
├── users.py             UserFactory, TeamFactory, RoleFactory, etc.
├── brands.py            BrandFactory, BrandContactFactory
├── campaigns.py         CampaignFactory
├── deliverables.py      DeliverableFactory
├── media.py             MediaFactory
├── payments.py          PaymentFactory, InvoiceFactory
└── auth.py              OAuth factories
```

## Key Classes & Services

### Dependency Injection (app/utils/providers.py)
- `provide_transaction()` - Database session with RLS + soft delete
- `provide_team_id()` - Current team from session
- `provide_campaign_id()` - Current campaign from session
- `provide_viewer_store()` - Thread viewer cache
- `provide_action_registry()` - Action availability
- `provide_object_registry()` - Object type registry

### Important Services
- `ThreadViewerStore` - In-memory viewer tracking for threads
- `ActionRegistry` - Determines available actions per object
- `ObjectRegistry` - Maps object types to handlers
- `ActionGroupType` - Enum of action groups (BrandActions, CampaignActions, etc.)

### Authentication Guards
- `@requires_user_id` - Must be authenticated
- `@requires_superuser` - Admin only
- `@requires_user_scope` - Team/campaign scope required

## Existing Test Patterns

### Async Test Pattern
```python
@pytest.mark.asyncio
async def test_something(memory_store: MemoryStore) -> None:
    store = ThreadViewerStore(store=memory_store)
    await store.add_viewer(1, 101)
    assert await store.get_viewers(1) == {101}
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input_val,expected", [(2, 4), (3, 9)])
def test_square(input_val, expected):
    assert square(input_val) == expected
```

### Factory Usage (from test_factory.py)
```python
from tests.factories.brands import BrandFactory

brand = BrandFactory.build()  # No DB required
# or with DB:
brand = await BrandFactory.create(session=db_session)
```

## Files to Examine First

For understanding how to write endpoint tests, examine:

1. **Route Structure:**
   - `/backend/app/users/routes.py` - Simple CRUD + authentication
   - `/backend/app/brands/routes.py` - CRUD with SQID encoding
   - `/backend/app/auth/routes.py` - Auth-specific logic

2. **Models:**
   - `/backend/app/users/models.py` - User, Team, Role
   - `/backend/app/brands/models.py` - Brand, BrandContact
   - `/backend/app/base/models.py` - Base model with RLS support

3. **Schemas:**
   - `/backend/app/users/schemas.py` - Request/response schemas
   - `/backend/app/brands/schemas.py` - Data models for serialization

4. **Database Setup:**
   - `/backend/app/index.py` - App configuration, SQLAlchemy setup
   - `/backend/app/utils/providers.py` - Dependency injection

## Quick Command Reference

```bash
# Install dependencies
make install

# Run existing tests
make test

# Type check
make check-backend

# Start PostgreSQL for integration tests
make db-start

# Start development server
make dev

# Code generation (after route changes)
make codegen
```

## Test Execution Examples

### Run all tests
```bash
cd backend && pytest
```

### Run specific test file
```bash
cd backend && pytest tests/test_event_consumers.py
```

### Run specific test class
```bash
cd backend && pytest tests/test_event_consumers.py::TestParseEventDataToUpdated
```

### Run specific test with output
```bash
cd backend && pytest tests/test_event_consumers.py::TestParseEventDataToUpdated::test_parse_valid_event_data -v
```

### Run with coverage
```bash
cd backend && pytest --cov=app --cov-report=html tests/
```

### Run async tests with debugging
```bash
cd backend && pytest -v -s tests/test_thread_viewer_store.py
```

## Priority Testing Order

1. **Auth routes** - `/auth/*` (foundational)
2. **User management** - `/users/*` (core)
3. **Team/Campaign scope** - Team switching, RLS isolation
4. **Brand CRUD** - `/brands/*` (main business entity)
5. **Campaign CRUD** - `/campaigns/*` (main business entity)
6. **Threads/Messaging** - `/threads/*` (real-time)
7. **Everything else** - Other features

## Common SQID Usage Pattern

```python
# In routes: parameter type is str
@get("/{id:str}")
async def get_brand(id: Sqid, ...):  # Automatically decoded
    # id is now an integer via type hook
    brand = await get_or_404(transaction, Brand, id)

# In tests:
from app.utils.sqids import sqid_encode
url = f"/brands/{sqid_encode(brand.id)}"
response = await client.get(url)
```

## Database Transaction Pattern in Routes

```python
@post("/{id:str}")
async def update_brand(
    id: Sqid,
    data: BrandUpdateSchema,
    request: Request,
    transaction: AsyncSession  # <- Injected transaction
) -> BrandSchema:
    brand = await get_or_404(transaction, Brand, id)
    # Make changes
    brand.name = data.name
    # Changes auto-commit when context manager exits
```

## Key Configuration

### Database (in app/utils/configure.py)
- `ASYNC_DATABASE_URL` - Async connection string
- `PSYCOPG_DATABASE_URL` - PostgreSQL connection (for sessions)

### Environment Variables Needed for Tests
- `DATABASE_URL` or `ASYNC_DATABASE_URL`
- `ENV=development` (for local testing)

## Example: Simple Brand Test Structure

```python
# tests/routes/test_brands.py
import pytest
from httpx import AsyncClient
from app.brands.models import Brand
from tests.factories.brands import BrandFactory

class TestBrandCRUD:
    async def test_get_brand(self, client: AsyncClient, brand: Brand):
        """GET /brands/{id} returns brand."""
        from app.utils.sqids import sqid_encode
        response = await client.get(f"/brands/{sqid_encode(brand.id)}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == brand.name
    
    async def test_update_brand(self, client: AsyncClient, brand: Brand):
        """POST /brands/{id} updates brand."""
        from app.utils.sqids import sqid_encode
        response = await client.post(
            f"/brands/{sqid_encode(brand.id)}",
            json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
    
    async def test_get_nonexistent_returns_404(self, client: AsyncClient):
        """GET /brands/{bad-id} returns 404."""
        response = await client.get("/brands/invalid")
        assert response.status_code == 404
```

## Debug Tips

### Check conftest fixtures available
```bash
cd backend && pytest --fixtures tests/
```

### See what tests pytest found
```bash
cd backend && pytest --collect-only tests/
```

### Run with detailed output
```bash
cd backend && pytest -vv -s tests/test_file.py
```

### Print statements in tests
```python
def test_something():
    result = some_function()
    print(f"Result: {result}")  # Shows when run with -s flag
    assert result == expected
```

### Inspect database state in test
```python
async def test_with_db_inspection(transaction: AsyncSession):
    # Make changes
    brand = await BrandFactory.create(session=transaction)
    
    # Inspect
    result = await transaction.execute(select(Brand).where(Brand.id == brand.id))
    db_brand = result.scalar_one()
    assert db_brand.name == brand.name
```

---

**Documentation:** See `BACKEND_TESTING_SUMMARY.md` for comprehensive guide
