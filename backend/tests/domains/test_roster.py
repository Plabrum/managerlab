"""Tests for roster domain: endpoints and basic operations."""

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.roster.models import Roster
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import assert_rls_isolated, execute_action, get_available_actions
from tests.factories.users import RosterFactory, UserFactory


class TestRoster:
    """Tests for roster endpoints."""

    async def test_get_roster(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /roster/{id} returns roster member details."""
        client, user_data = authenticated_client

        # Create a roster member for this team
        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            user_id=user_data["user_id"],
        )
        await db_session.commit()

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
        db_session: AsyncSession,
    ):
        """Test POST /roster/{id} updates roster member."""
        client, user_data = authenticated_client

        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            user_id=user_data["user_id"],
            name="Original Name",
        )
        await db_session.commit()

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
        db_session: AsyncSession,
    ):
        """Test GET /actions/roster_actions/{id} returns available actions."""
        client, user_data = authenticated_client

        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            user_id=user_data["user_id"],
        )
        await db_session.commit()

        # Get available actions using SQID-encoded ID
        actions = await get_available_actions(client, "roster_actions", sqid_encode(roster.id))

        # Should have at least update and delete actions
        action_keys = [action["action"] for action in actions]
        assert "roster.update" in action_keys
        assert "roster.delete" in action_keys

    async def test_execute_roster_update_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing roster update action."""
        client, user_data = authenticated_client

        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            user_id=user_data["user_id"],
            name="Before Update",
        )
        await db_session.commit()

        # Execute update action using SQID-encoded ID
        response = await execute_action(
            client,
            "roster_actions",
            "roster.update",
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
        db_session: AsyncSession,
    ):
        """Test executing roster delete action."""
        client, user_data = authenticated_client

        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            user_id=user_data["user_id"],
        )
        await db_session.commit()
        roster_id = roster.id

        # Execute delete action using SQID-encoded ID
        response = await execute_action(
            client,
            "roster_actions",
            "roster.delete",
            obj_id=sqid_encode(roster.id),
        )

        assert response.status_code in [200, 201, 204]

        # Verify the roster member was soft-deleted
        db_session.expire(roster)
        result = await db_session.execute(select(Roster).where(Roster.id == roster_id))
        deleted_roster = result.scalar_one_or_none()
        # With soft delete, the roster should still exist but be marked as deleted
        assert deleted_roster is not None
        assert deleted_roster.deleted_at is not None

    async def test_roster_rls_isolation(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
        multi_team_setup: dict,
    ):
        """Test that roster members are properly isolated by team."""
        client, user_data = authenticated_client

        # Create a roster member for team2 (need to create a user for team2 first)
        team2_user = await UserFactory.create_async(session=db_session)
        await db_session.commit()

        team2_roster = await RosterFactory.create_async(
            session=db_session,
            team_id=multi_team_setup["team2"].id,
            user_id=team2_user.id,
        )
        await db_session.commit()

        # Try to access team2's roster member with team1's client
        await assert_rls_isolated(client, f"/roster/{sqid_encode(team2_roster.id)}")

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
        db_session: AsyncSession,
    ):
        """Test updating roster with social media handles."""
        client, user_data = authenticated_client

        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            user_id=user_data["user_id"],
        )
        await db_session.commit()

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
