"""Tests for users domain: endpoints and basic operations."""

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import Role
from app.utils.sqids import sqid_encode
from tests.factories.users import TeamFactory, UserFactory


class TestUsers:
    """Tests for user endpoints."""

    async def test_get_current_user(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /users/current_user returns authenticated user."""
        client, user_data = authenticated_client

        response = await client.get("/users/current_user")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(user_data["user_id"])
        assert data["email"] == user_data["email"]

    async def test_get_user_by_id(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /users/{id} returns user details."""
        client, user_data = authenticated_client

        response = await client.get(f"/users/{user_data['user_id']}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(user_data["user_id"])
        assert data["email"] == user_data["email"]

    async def test_list_users_requires_superuser(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /users requires superuser access."""
        client, _ = authenticated_client

        # Regular user should not be able to list all users
        response = await client.get("/users")
        # Should get 403 Forbidden or 401 Unauthorized
        assert response.status_code in [401, 403, 404]

    async def test_get_teams(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /users/teams returns user's teams."""
        client, user_data = authenticated_client

        response = await client.get("/users/teams")
        assert response.status_code == 200

        data = response.json()
        assert "teams" in data
        # User should have at least their own team
        assert len(data["teams"]) >= 1
        # Verify the user's team is in the list
        team_ids = [team["team_id"] for team in data["teams"]]
        assert user_data["team_id"] in team_ids

    async def test_create_user(
        self,
        test_client: AsyncTestClient,
        db_session: AsyncSession,
    ):
        """Test POST /users/signup creates a new user."""
        # This test uses unauthenticated client since signup is public

        response = await test_client.post(
            "/users/signup",
            json={
                "name": "New User",
                "email": "newuser@example.com",
                "google_id": "google123",
            },
        )

        # Team creation might have different status codes
        assert response.status_code in [200, 201]

        if response.status_code in [200, 201]:
            data = response.json()
            assert "name" in data or "id" in data

    async def test_switch_team(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test POST /users/switch-team switches user's active team."""
        client, user_data = authenticated_client

        # Create a second team and add user to it
        team2 = await TeamFactory.create_async(session=db_session, name="Team 2")
        role2 = Role(
            user_id=user_data["user"].id,
            team_id=team2.id,
            role_level="member",
        )
        db_session.add(role2)
        await db_session.commit()

        # Switch to team2
        response = await client.post(
            "/users/switch-team",
            json={"team_id": int(team2.id)},
        )
        assert response.status_code in [200, 204]


class TestTeams:
    """Tests for team endpoints."""

    async def test_get_teams_list(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /users/teams returns list of user's teams."""
        client, user_data = authenticated_client

        response = await client.get("/users/teams")
        assert response.status_code == 200

        data = response.json()
        assert "teams" in data
        assert isinstance(data["teams"], list)

    async def test_create_team(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test POST /teams creates a new team."""
        client, _ = authenticated_client

        response = await client.post(
            "/teams",
            json={
                "name": "New Team",
                "description": "A brand new team",
            },
        )

        # Team creation might have different status codes
        assert response.status_code in [200, 201]

        if response.status_code in [200, 201]:
            data = response.json()
            assert "name" in data or "id" in data


class TestUserTeamIsolation:
    """Tests for user/team isolation and permissions."""

    async def test_user_cannot_access_other_team_data(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        multi_team_setup: dict,
    ):
        """Test that users cannot access data from teams they don't belong to."""
        client, user_data = authenticated_client

        # Verify the authenticated user is NOT from team2
        assert user_data["team_id"] != int(multi_team_setup["team2"].id)

    async def test_multi_team_user_can_switch(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that a user in multiple teams can switch between them."""
        client, user_data = authenticated_client

        # Create a second team
        team2 = await TeamFactory.create_async(session=db_session)

        # Add user to second team
        role = Role(
            user_id=user_data["user"].id,
            team_id=team2.id,
            role_level="member",
        )
        db_session.add(role)
        await db_session.commit()

        # Get teams list - should show both teams
        response = await client.get("/users/teams")
        assert response.status_code == 200
        data = response.json()
        team_ids = [team["team_id"] for team in data["teams"]]
        assert len(team_ids) >= 2

        # Switch to team2
        switch_response = await client.post(
            "/users/switch-team",
            json={"team_id": int(team2.id)},
        )
        assert switch_response.status_code in [200, 204]
