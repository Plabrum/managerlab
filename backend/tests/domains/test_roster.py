"""Tests for roster domain: endpoints and basic operations."""

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.roster.models import Roster
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import execute_action, get_available_actions
from tests.factories.users import RosterFactory, UserFactory  # Still needed for specific tests


class TestRoster:
    """Tests for roster endpoints."""

    async def test_get_roster(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        roster,
    ):
        """Test GET /roster/{id} returns roster member details."""
        client, user_data = authenticated_client

        # Get the roster member
        response = await client.get(f"/roster/{sqid_encode(roster.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(roster.id)
        assert data["name"] == roster.name
        assert data["team_id"] == sqid_encode(user_data["team_id"])
        assert "actions" in data  # Should include available actions

    async def test_update_roster(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        roster,
    ):
        """Test POST /roster/{id} updates roster member."""
        client, user_data = authenticated_client

        # Update the roster member
        response = await client.post(
            f"/roster/{sqid_encode(roster.id)}",
            json={"name": "Updated Name"},
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert data["name"] == "Updated Name"

    async def test_list_roster_actions(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        roster,
    ):
        """Test GET /actions/roster_actions/{id} returns available actions."""
        client, user_data = authenticated_client

        # Get available actions using SQID-encoded ID
        actions = await get_available_actions(client, "roster_actions", sqid_encode(roster.id))

        # Should have at least update and delete actions
        action_keys = [action["action"] for action in actions]
        assert "roster_actions__roster_update" in action_keys
        assert "roster_actions__roster_delete" in action_keys

    async def test_execute_roster_update_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        roster,
        db_session: AsyncSession,
    ):
        """Test executing roster update action."""
        client, user_data = authenticated_client

        # Execute update action using SQID-encoded ID
        response = await execute_action(
            client,
            "roster_actions",
            "roster_actions__roster_update",
            data={"name": "After Update", "email": "newemail@example.com"},
            obj_id=sqid_encode(roster.id),
        )

        assert response.status_code in [200, 201, 204]

        # Verify the roster member was updated
        await db_session.refresh(roster)
        assert roster.name == "After Update"
        assert roster.email == "newemail@example.com"

    async def test_execute_roster_delete_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        roster,
        db_session: AsyncSession,
    ):
        """Test executing roster delete action."""
        client, user_data = authenticated_client
        roster_id = roster.id

        # Execute delete action using SQID-encoded ID
        response = await execute_action(
            client,
            "roster_actions",
            "roster_actions__roster_delete",
            obj_id=sqid_encode(roster.id),
        )

        assert response.status_code in [200, 201, 204]

        # Verify the roster member was soft-deleted
        # Use raw SQL to bypass the soft delete filter
        from sqlalchemy import text

        result = await db_session.execute(text("SELECT deleted_at FROM roster WHERE id = :id"), {"id": roster_id})
        row = result.fetchone()
        # With soft delete, the roster should still exist but be marked as deleted
        assert row is not None
        assert row[0] is not None  # deleted_at should be set

    async def test_get_roster_not_found(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /roster/{id} returns 404 for non-existent roster member."""
        client, _ = authenticated_client

        # Use a valid SQID for a non-existent ID
        fake_id = sqid_encode(999999999)
        response = await client.get(f"/roster/{fake_id}")
        assert response.status_code == 404

    async def test_update_roster_with_social_handles(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        roster,
    ):
        """Test updating roster with social media handles."""
        client, user_data = authenticated_client

        # Update with social handles
        response = await client.post(
            f"/roster/{sqid_encode(roster.id)}",
            json={
                "instagram_handle": "@influencer",
                "tiktok_handle": "@tiktoker",
                "youtube_channel": "UCxyz123",
            },
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert data["instagram_handle"] == "@influencer"
        assert data["tiktok_handle"] == "@tiktoker"
        assert data["youtube_channel"] == "UCxyz123"
