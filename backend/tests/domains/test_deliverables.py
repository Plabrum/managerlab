"""Tests for deliverables domain: endpoints and operations."""

from datetime import date, datetime, timedelta, timezone

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.deliverables.enums import DeliverableStates, DeliverableType, SocialMediaPlatforms
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import assert_rls_isolated, execute_action, get_available_actions
from tests.factories.deliverables import DeliverableFactory


class TestDeliverables:
    """Tests for deliverable endpoints."""

    async def test_get_deliverable(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /deliverables/{id} returns deliverable details."""
        client, user_data = authenticated_client

        # Create a deliverable for this team
        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Get the deliverable
        response = await client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(deliverable.id)
        assert data["title"] == deliverable.title
        assert data["team_id"] == sqid_encode(user_data["team_id"])
        assert "actions" in data  # Should include available actions

    async def test_update_deliverable(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test POST /deliverables/{id} updates deliverable."""
        client, user_data = authenticated_client

        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            title="Original Title",
            content="Original content",
        )
        await db_session.commit()

        # Update the deliverable
        response = await client.post(
            f"/deliverables/{sqid_encode(deliverable.id)}",
            json={
                "title": "Updated Title",
                "content": "Updated content",
            },
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated content"

    async def test_update_deliverable_caption_requirements(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test updating deliverable caption requirements."""
        client, user_data = authenticated_client

        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            handles=[],
            hashtags=[],
        )
        await db_session.commit()

        # Update caption requirements
        response = await client.post(
            f"/deliverables/{sqid_encode(deliverable.id)}",
            json={
                "handles": ["@brand", "@partner"],
                "hashtags": ["#ad", "#sponsored"],
                "disclosures": ["Paid partnership"],
            },
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert "@brand" in data["handles"]
        assert "#ad" in data["hashtags"]
        assert "Paid partnership" in data["disclosures"]

    async def test_list_deliverable_actions(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /actions/deliverable_actions/{id} returns available actions."""
        client, user_data = authenticated_client

        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Get available actions
        actions = await get_available_actions(client, "deliverable_actions", sqid_encode(deliverable.id))

        # Should have at least update and delete actions
        action_keys = [action["action"] for action in actions]
        assert "deliverable.update" in action_keys
        assert "deliverable.delete" in action_keys

    async def test_execute_deliverable_update_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing deliverable update action."""
        client, user_data = authenticated_client

        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            title="Original Title",
        )
        await db_session.commit()

        # Execute update action
        result = await execute_action(
            client,
            "deliverable_actions",
            "deliverable.update",
            {"title": "Updated via Action"},
            sqid_encode(deliverable.id),
        )

        assert result["success"] is True

        # Verify the update
        await db_session.refresh(deliverable)
        assert deliverable.title == "Updated via Action"

    async def test_execute_deliverable_delete_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing deliverable delete action."""
        client, user_data = authenticated_client

        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Execute delete action
        result = await execute_action(
            client,
            "deliverable_actions",
            "deliverable.delete",
            {},
            sqid_encode(deliverable.id),
        )

        assert result["success"] is True

        # Verify soft deletion
        await db_session.refresh(deliverable)
        assert deliverable.deleted_at is not None

    async def test_deliverable_rls_isolation(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        other_team_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that teams cannot access each other's deliverables."""
        client, user_data = authenticated_client
        other_client, other_user_data = other_team_client

        # Create deliverable for first team
        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Verify RLS isolation
        await assert_rls_isolated(
            client=other_client,
            resource_path=f"/deliverables/{sqid_encode(deliverable.id)}",
        )

    async def test_get_deliverable_not_found(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /deliverables/{id} with non-existent ID returns 404."""
        client, user_data = authenticated_client

        # Try to get a non-existent deliverable
        response = await client.get(f"/deliverables/{sqid_encode(99999)}")
        assert response.status_code == 404

    async def test_deliverable_with_campaign(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test deliverable associated with a campaign."""
        from tests.factories.campaigns import CampaignFactory

        client, user_data = authenticated_client

        # Create a campaign
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Create deliverable linked to campaign
        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            campaign_id=campaign.id,
        )
        await db_session.commit()

        # Get the deliverable
        response = await client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["campaign_id"] == sqid_encode(campaign.id)


class TestDeliverableStates:
    """Tests for deliverable state transitions."""

    async def test_deliverable_initial_state(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that new deliverables start in DRAFT state."""
        client, user_data = authenticated_client

        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        response = await client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        # State should be initial state (DRAFT)
        assert data["state"] in [
            DeliverableStates.DRAFT.value,
            DeliverableStates.IN_REVIEW.value,
        ]


class TestDeliverablePlatforms:
    """Tests for deliverable platform configurations."""

    async def test_deliverable_with_instagram_platform(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test deliverable configured for Instagram."""
        client, user_data = authenticated_client

        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            platforms=SocialMediaPlatforms.INSTAGRAM,
            deliverable_type=DeliverableType.INSTAGRAM_FEED_POST,
        )
        await db_session.commit()

        response = await client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["platforms"] == SocialMediaPlatforms.INSTAGRAM.value
        assert data["deliverable_type"] == DeliverableType.INSTAGRAM_FEED_POST.value

    async def test_deliverable_posting_dates(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test deliverable posting date fields."""
        client, user_data = authenticated_client

        posting_date = datetime.now(tz=timezone.utc) + timedelta(days=7)
        start_date = date.today() + timedelta(days=7)
        end_date = date.today() + timedelta(days=14)

        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            posting_date=posting_date,
            posting_start_date=start_date,
            posting_end_date=end_date,
        )
        await db_session.commit()

        response = await client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["posting_start_date"] == str(start_date)
        assert data["posting_end_date"] == str(end_date)

    async def test_deliverable_approval_settings(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test deliverable approval settings."""
        client, user_data = authenticated_client

        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            approval_required=True,
            approval_rounds=2,
        )
        await db_session.commit()

        response = await client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["approval_required"] is True
        assert data["approval_rounds"] == 2
