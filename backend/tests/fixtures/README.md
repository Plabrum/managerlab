# Test Fixtures

This directory contains organized pytest fixtures for the backend test suite.

## Structure

The fixtures are organized into logical modules for better maintainability:

### `database.py`
Database-related fixtures including:
- `test_config` - Test configuration (session-scoped)
- `test_engine` - Database engine with NullPool for isolation
- `setup_database` - Runs Alembic migrations for test schema
- `db_session` - Database session with system mode enabled for fixture creation
- `transaction` - Transaction with team-scoped RLS, event listeners, and rollback
- `memory_store` - Fresh MemoryStore instance

**Architecture:**
- `db_session` creates a session with system mode enabled (bypasses RLS) for creating test fixtures
- `transaction` uses `db_session` + `team`, sets RLS context, attaches event listeners, and handles rollback
- Rollback logic lives in `transaction`, not `db_session`
- Fixture-based tests use `transaction` directly; HTTP tests use `provide_test_transaction` (same RLS logic, different data sources)

### `dependencies.py`
Dependency injection providers and mock clients:
- `mock_s3_client` - Mocked S3 client for testing
- `mock_http_client` - Mocked HTTP client for testing
- `mock_email_client` - Mocked email client for testing
- `provide_test_transaction` - Reads team_id from session and sets RLS context for HTTP requests
- `provide_test_config` - Config provider for tests
- `provide_test_team_id` - Team ID provider for tests
- `provide_test_campaign_id` - Campaign ID provider for tests

**Note:** `provide_test_transaction` can't use the `transaction` fixture due to Litestar DI circular dependency. Instead, it reads `team_id` from `request.session` (set by `authenticated_client`) and applies the same RLS logic.

### `app.py`
Litestar application and test client fixtures:
- `test_app` - Configured Litestar app with test overrides
- `test_client` - Async test client for making HTTP requests

### `auth.py`
Authentication and authorization fixtures:
- `authenticated_client` - Sets session data using `user` and `team` fixtures for authentication
- `other_team_client` - Authenticated client for different team (RLS testing)
- `admin_client` - Authenticated admin client with admin role
- `multi_team_setup` - Multiple teams/users for RLS isolation testing

**Note:** `authenticated_client` now uses the `user` and `team` fixtures from `common.py`, ensuring consistency across all tests.

### `factories.py`
Factory helper fixtures for creating complex objects:
- `create_complete_campaign` - Create campaign with all dependencies
- `create_brand_with_contacts` - Create brand with multiple contacts
- `create_deliverable_with_media` - Create deliverable with media associations

### `common.py`
Common object fixtures for convenient testing:
- `team` - Creates a team for testing
- `user` - Creates a user linked to team with member role
- `brand` - Brand associated with team
- `campaign` - Campaign with brand
- `roster` - Roster member
- `deliverable` - Deliverable for campaign
- `document` - Document for team
- `invoice` - Invoice for team

**Note:** `team` and `user` are the foundational fixtures used by `authenticated_client` and the `transaction` fixture.

## Usage

All fixtures are automatically available to tests via pytest's fixture discovery. Simply declare them as test function parameters:

```python
async def test_example(authenticated_client: AsyncTestClient, user, team, brand):
    # authenticated_client is already authenticated with user and team
    response = await authenticated_client.get(f"/brands/{brand.id}")
    assert response.status_code == 200
```

## Benefits of This Structure

1. **Clear organization** - Fixtures are grouped by logical purpose
2. **No inline imports** - All imports are at the top of each file
3. **Easy to navigate** - Find fixtures by category
4. **Better maintainability** - Changes to one fixture type don't affect others
5. **Self-documenting** - Each module has a clear purpose
