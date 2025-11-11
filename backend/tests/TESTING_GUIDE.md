# Backend Testing Guide

This guide explains how to write comprehensive endpoint tests for the ManagerLab backend using Litestar's testing framework.

## Table of Contents
- [Quick Start](#quick-start)
- [Test Fixtures Overview](#test-fixtures-overview)
- [Writing Endpoint Tests](#writing-endpoint-tests)
- [Testing Patterns](#testing-patterns)
- [Running Tests](#running-tests)

## Quick Start

### Basic Endpoint Test
```python
import pytest

async def test_health_endpoint(test_client):
    """Test the health check endpoint."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["detail"] == "ok"
```

### Authenticated Endpoint Test
```python
async def test_get_current_user(authenticated_client):
    """Test getting the current authenticated user."""
    client, user = authenticated_client

    response = await client.get("/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["user_id"]
    assert data["email"] == user["email"]
```

## Test Fixtures Overview

All fixtures are defined in `backend/tests/conftest.py`.

### Database Fixtures

#### `db_session`
Provides a clean database session for each test with automatic rollback.
```python
async def test_create_user(db_session):
    from tests.factories.user_factory import UserFactory

    user = await UserFactory.create_async(
        session=db_session,
        email="test@example.com"
    )

    assert user.id is not None
    assert user.email == "test@example.com"
```

**Key Features:**
- Function-scoped (new session per test)
- Automatic rollback after test (no pollution)
- Soft delete filter enabled
- Based on SQLite in-memory by default (fast!)

#### `test_db_url`
The database URL used for testing. Override for PostgreSQL-specific tests:
```python
@pytest.fixture(scope="module")
def test_db_url():
    """Use real PostgreSQL for these tests."""
    return "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
```

### HTTP Client Fixtures

#### `test_client`
Unauthenticated async HTTP client for testing public endpoints.
```python
async def test_public_endpoint(test_client):
    response = await test_client.get("/health")
    assert response.status_code == 200
```

#### `authenticated_client`
HTTP client with a logged-in user + team.
```python
async def test_protected_endpoint(authenticated_client):
    client, user = authenticated_client

    # user dict contains: user_id, team_id, email, team, user
    response = await client.get(f"/teams/{user['team_id']}")
    assert response.status_code == 200
```

#### `admin_client`
HTTP client with admin privileges.
```python
async def test_admin_endpoint(admin_client):
    client, admin = admin_client

    response = await client.get("/admin/dashboard")
    assert response.status_code == 200
```

### Configuration Fixtures

#### `test_config`
Test configuration with safe defaults (no real AWS credentials, etc.).
```python
async def test_config_usage(test_config):
    assert test_config.ENV == "testing"
    assert test_config.IS_DEV is False
```

#### `mock_s3_client`
Mocked S3 client for testing file uploads without hitting AWS.
```python
async def test_file_upload(authenticated_client, mock_s3_client):
    client, user = authenticated_client

    # Upload will use the mock
    response = await client.post("/media/upload", files={"file": ("test.jpg", b"data")})

    # Verify mock was called
    mock_s3_client.upload_file.assert_called_once()
```

#### `mock_http_client`
Mocked aiohttp client for testing external API calls.

### RLS (Row-Level Security) Fixtures

#### `multi_team_setup`
Creates two teams with users for testing cross-team isolation.
```python
async def test_team_isolation(authenticated_client, multi_team_setup, db_session):
    from tests.factories.document_factory import DocumentFactory

    client, user = authenticated_client
    teams = multi_team_setup

    # Create document for team2
    doc = await DocumentFactory.create_async(
        session=db_session,
        team_id=teams["team2"].id,
        name="Secret Document"
    )
    await db_session.commit()

    # User from team1 should NOT see team2's document
    response = await client.get(f"/documents/{doc.id}")
    assert response.status_code == 404  # RLS blocks access
```

## Writing Endpoint Tests

### Test Structure

Organize tests by domain in `backend/tests/test_endpoints/`:
```
backend/tests/
├── conftest.py              # Shared fixtures
├── test_endpoints/          # Endpoint tests by domain
│   ├── test_users.py
│   ├── test_teams.py
│   ├── test_documents.py
│   └── ...
└── TESTING_GUIDE.md         # This file
```

### CRUD Test Template

```python
"""Tests for User endpoints."""
import pytest
from tests.factories.user_factory import UserFactory


class TestUserEndpoints:
    """Test suite for /users endpoints."""

    # CREATE
    async def test_create_user(self, authenticated_client, db_session):
        """Test POST /users to create a new user."""
        client, auth_user = authenticated_client

        payload = {
            "email": "newuser@example.com",
            "name": "New User",
        }

        response = await client.post("/users", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["name"] == payload["name"]
        assert data["team_id"] == auth_user["team_id"]

    # READ (list)
    async def test_list_users(self, authenticated_client, db_session):
        """Test GET /users to list all users in team."""
        client, user = authenticated_client

        # Create additional users in the same team
        await UserFactory.create_batch_async(
            size=3,
            session=db_session,
            team_id=user["team_id"]
        )
        await db_session.commit()

        response = await client.get("/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4  # Auth user + 3 created

    # READ (detail)
    async def test_get_user(self, authenticated_client, db_session):
        """Test GET /users/{id} to get a specific user."""
        client, user = authenticated_client

        target_user = await UserFactory.create_async(
            session=db_session,
            team_id=user["team_id"],
            email="target@example.com"
        )
        await db_session.commit()

        response = await client.get(f"/users/{target_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == target_user.id
        assert data["email"] == "target@example.com"

    # UPDATE
    async def test_update_user(self, authenticated_client, db_session):
        """Test PATCH /users/{id} to update a user."""
        client, user = authenticated_client

        target_user = await UserFactory.create_async(
            session=db_session,
            team_id=user["team_id"],
            name="Old Name"
        )
        await db_session.commit()

        payload = {"name": "New Name"}
        response = await client.patch(f"/users/{target_user.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"

    # DELETE
    async def test_delete_user(self, authenticated_client, db_session):
        """Test DELETE /users/{id} to delete a user."""
        client, user = authenticated_client

        target_user = await UserFactory.create_async(
            session=db_session,
            team_id=user["team_id"]
        )
        await db_session.commit()

        response = await client.delete(f"/users/{target_user.id}")

        assert response.status_code == 204

        # Verify it's gone (or soft-deleted)
        get_response = await client.get(f"/users/{target_user.id}")
        assert get_response.status_code == 404
```

## Testing Patterns

### 1. Testing Authentication

#### Unauthenticated Access
```python
async def test_requires_authentication(test_client):
    """Test that endpoint requires authentication."""
    response = await test_client.get("/users/me")
    assert response.status_code == 401  # Unauthorized
```

#### Wrong User Access
```python
async def test_cannot_access_other_user_data(authenticated_client, db_session):
    """Test that users cannot access other users' private data."""
    client, user = authenticated_client

    # Create another user in the same team
    other_user = await UserFactory.create_async(
        session=db_session,
        team_id=user["team_id"]
    )
    await db_session.commit()

    # Try to update the other user (should fail)
    response = await client.patch(
        f"/users/{other_user.id}/private-settings",
        json={"setting": "value"}
    )
    assert response.status_code == 403  # Forbidden
```

### 2. Testing RLS (Team Isolation)

```python
async def test_team_isolation(authenticated_client, multi_team_setup, db_session):
    """Test that users can only see their team's data."""
    from tests.factories.document_factory import DocumentFactory

    client, user = authenticated_client
    teams = multi_team_setup

    # Create documents for both teams
    team1_doc = await DocumentFactory.create_async(
        session=db_session,
        team_id=teams["team1"].id,
        name="Team 1 Doc"
    )
    team2_doc = await DocumentFactory.create_async(
        session=db_session,
        team_id=teams["team2"].id,
        name="Team 2 Doc"
    )
    await db_session.commit()

    # User should only see their team's document in list
    response = await client.get("/documents")
    assert response.status_code == 200

    doc_ids = [doc["id"] for doc in response.json()]
    assert team1_doc.id in doc_ids or team2_doc.id in doc_ids  # Depending on which team user is in

    # User should NOT be able to access other team's document directly
    other_team_doc_id = team2_doc.id if user["team_id"] == teams["team1"].id else team1_doc.id
    response = await client.get(f"/documents/{other_team_doc_id}")
    assert response.status_code == 404  # RLS makes it look like it doesn't exist
```

### 3. Testing Validation

```python
async def test_invalid_input_validation(authenticated_client):
    """Test that invalid input returns proper error."""
    client, user = authenticated_client

    # Missing required field
    payload = {
        # "email": "test@example.com",  # Required field missing
        "name": "Test User"
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 400  # Bad Request
    error = response.json()
    assert "email" in str(error).lower()  # Error mentions missing field

async def test_email_format_validation(authenticated_client):
    """Test that invalid email format is rejected."""
    client, user = authenticated_client

    payload = {
        "email": "not-an-email",  # Invalid format
        "name": "Test User"
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 400
    error = response.json()
    assert "email" in str(error).lower()
```

### 4. Testing Error Cases

```python
async def test_not_found_error(authenticated_client):
    """Test 404 for non-existent resource."""
    client, user = authenticated_client

    response = await client.get("/users/999999")

    assert response.status_code == 404
    error = response.json()
    assert "not found" in error["detail"].lower()

async def test_conflict_error(authenticated_client, db_session):
    """Test 409 for duplicate resource."""
    from tests.factories.user_factory import UserFactory

    client, user = authenticated_client

    # Create user with specific email
    existing = await UserFactory.create_async(
        session=db_session,
        team_id=user["team_id"],
        email="duplicate@example.com"
    )
    await db_session.commit()

    # Try to create another user with same email
    payload = {
        "email": "duplicate@example.com",
        "name": "Duplicate User"
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 409  # Conflict
```

### 5. Testing Actions/Custom Endpoints

```python
async def test_custom_action(authenticated_client, db_session):
    """Test custom action endpoint."""
    from tests.factories.document_factory import DocumentFactory

    client, user = authenticated_client

    # Create document
    doc = await DocumentFactory.create_async(
        session=db_session,
        team_id=user["team_id"],
        status="draft"
    )
    await db_session.commit()

    # Perform action
    response = await client.post(f"/documents/{doc.id}/publish")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
```

### 6. Testing File Uploads

```python
async def test_file_upload(authenticated_client, mock_s3_client):
    """Test file upload endpoint."""
    client, user = authenticated_client

    # Create fake file data
    file_content = b"fake image data"
    files = {
        "file": ("test.jpg", file_content, "image/jpeg")
    }

    response = await client.post("/media/upload", files=files)

    assert response.status_code == 201
    data = response.json()
    assert "url" in data
    assert "key" in data

    # Verify S3 mock was called
    mock_s3_client.upload_file.assert_called_once()
```

## Running Tests

### Run All Tests
```bash
make test
```

### Run Specific Test File
```bash
pytest backend/tests/test_endpoints/test_users.py
```

### Run Specific Test
```bash
pytest backend/tests/test_endpoints/test_users.py::TestUserEndpoints::test_create_user
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html backend/tests/
```

### Run in Verbose Mode
```bash
pytest -v backend/tests/
```

### Run Tests Matching Pattern
```bash
pytest -k "test_create" backend/tests/
```

## Tips & Best Practices

### 1. Use Factories for Test Data
Always use factories instead of creating models manually:
```python
# ✅ Good
user = await UserFactory.create_async(session=db_session, email="test@example.com")

# ❌ Bad
user = User(email="test@example.com", team_id=1, created_at=datetime.now(tz=timezone.utc))
session.add(user)
await session.flush()
```

### 2. Test One Thing Per Test
Each test should verify one specific behavior:
```python
# ✅ Good
async def test_create_user_returns_201(authenticated_client):
    """Test that creating a user returns 201 status."""
    # Test only the status code

async def test_create_user_returns_correct_data(authenticated_client):
    """Test that created user has correct data."""
    # Test only the response data

# ❌ Bad
async def test_create_user(authenticated_client):
    """Test creating a user."""
    # Test status code, response data, database state, side effects, etc.
```

### 3. Use Descriptive Test Names
Test names should clearly describe what they test:
```python
# ✅ Good
async def test_cannot_delete_user_from_different_team(authenticated_client):
    """Test that users cannot delete users from other teams."""

# ❌ Bad
async def test_delete_user(authenticated_client):
    """Test delete user."""
```

### 4. Arrange-Act-Assert Pattern
Structure tests clearly:
```python
async def test_update_user_name(authenticated_client, db_session):
    # Arrange: Set up test data
    client, user = authenticated_client
    target_user = await UserFactory.create_async(
        session=db_session,
        team_id=user["team_id"],
        name="Old Name"
    )
    await db_session.commit()

    # Act: Perform the action
    response = await client.patch(
        f"/users/{target_user.id}",
        json={"name": "New Name"}
    )

    # Assert: Verify the results
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
```

### 5. Don't Test Framework Code
Focus on your business logic, not Litestar's internals:
```python
# ✅ Good: Test your business logic
async def test_user_cannot_have_duplicate_email(authenticated_client):
    """Test that the system prevents duplicate emails."""

# ❌ Bad: Test framework behavior
async def test_litestar_returns_json(test_client):
    """Test that Litestar returns JSON."""  # This is testing the framework
```

## Next Steps

1. **Create test files** for each domain in `backend/tests/test_endpoints/`
2. **Start with simple endpoints** like health checks and GET requests
3. **Add CRUD tests** for each resource (Create, Read, Update, Delete)
4. **Add authorization tests** to verify RLS and permissions
5. **Add validation tests** for input validation
6. **Add error case tests** for edge cases and error handling
7. **Monitor coverage** and aim for 80%+ coverage on critical paths

For more information:
- Litestar Testing Docs: https://docs.litestar.dev/2/usage/testing.html
- Pytest Async: https://pytest-asyncio.readthedocs.io/
- Factory Pattern: Review `backend/tests/factories/` for examples
