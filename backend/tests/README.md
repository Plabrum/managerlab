# Backend Test Infrastructure

Comprehensive testing infrastructure for the ManagerLab backend, built using Litestar's testing framework and pytest.

## Quick Start

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_endpoints/test_users.py

# Run with coverage
pytest --cov=app --cov-report=html tests/

# Run specific test
pytest tests/test_endpoints/test_users.py::test_create_user
```

## Files

- **`conftest.py`** - All pytest fixtures (database, HTTP clients, auth, mocks)
- **`TESTING_GUIDE.md`** - Comprehensive guide with patterns and examples
- **`test_fixtures_demo.py`** - Live examples demonstrating all fixtures
- **`factories/`** - Data factories for creating test objects

## Available Fixtures

### HTTP Clients
- `test_client` - Unauthenticated client for public endpoints
- `authenticated_client` - Client with logged-in user + team
- `admin_client` - Client with admin privileges

### Database
- `db_session` - Clean database session with auto-rollback
- `test_db_url` - PostgreSQL test database URL
- `multi_team_setup` - Multiple teams for RLS testing

### Configuration & Mocks
- `test_config` - Safe test configuration
- `mock_s3_client` - Mocked S3 for file operations
- `mock_http_client` - Mocked HTTP client for external APIs

## Example Test

```python
import pytest

pytestmark = pytest.mark.asyncio


async def test_create_user(authenticated_client):
    """Test creating a new user."""
    client, user = authenticated_client

    payload = {
        "email": "newuser@example.com",
        "name": "New User"
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]
```

## Documentation

See **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** for:
- Detailed fixture documentation
- CRUD test templates
- Testing patterns (auth, RLS, validation, errors)
- Best practices

## Architecture

- **Framework**: Litestar testing + pytest-asyncio
- **Database**: PostgreSQL (same as dev environment)
- **Isolation**: Each test gets a clean session with automatic rollback
- **Authentication**: Session-based auth matching production
- **Factories**: Polyfactory for generating test data

## Next Steps

1. Create `test_endpoints/` directory
2. Add test files for each domain (users, teams, documents, etc.)
3. Start with simple GET tests, then add CRUD tests
4. Add RLS tests to verify team isolation
5. Add validation and error handling tests

## Tips

- Always use `pytestmark = pytest.mark.asyncio` for async tests
- Use factories from `tests/factories/` to create test data
- Follow the AAA pattern: Arrange, Act, Assert
- Test one behavior per test function
- See `test_fixtures_demo.py` for live examples
