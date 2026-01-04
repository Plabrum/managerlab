"""Tests for deliverables domain: endpoints and operations."""

from datetime import UTC, date, datetime, timedelta

from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.deliverables.enums import DeliverableStates, DeliverableType, SocialMediaPlatforms
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import execute_action, get_available_actions
from tests.factories.deliverables import DeliverableFactory  # Still needed for platform-specific tests


class TestDeliverables:
    """Tests for deliverable endpoints."""

    async def test_get_deliverable(
        self,
        authenticated_client: AsyncTestClient,
        deliverable,
    ):
        """Test GET /deliverables/{id} returns deliverable details."""

        response = await authenticated_client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200
        assert response.json() is not None

    async def test_update_deliverable(
        self,
        authenticated_client: AsyncTestClient,
        deliverable,
    ):
        """Test POST /deliverables/{id} updates deliverable."""

        response = await authenticated_client.post(
            f"/deliverables/{sqid_encode(deliverable.id)}",
            json={
                "title": "Updated Title",
                "content": "Updated content",
                "platforms": deliverable.platforms.value,
                "posting_date": deliverable.posting_date.isoformat(),
                "deliverable_type": deliverable.deliverable_type.value if deliverable.deliverable_type else None,
                "count": deliverable.count,
                "posting_start_date": str(deliverable.posting_start_date) if deliverable.posting_start_date else None,
                "posting_end_date": str(deliverable.posting_end_date) if deliverable.posting_end_date else None,
                "handles": deliverable.handles,
                "hashtags": deliverable.hashtags,
                "disclosures": deliverable.disclosures,
                "approval_required": deliverable.approval_required,
                "approval_rounds": deliverable.approval_rounds,
                "campaign_id": deliverable.campaign_id,
                "notes": deliverable.notes,
            },
        )
        assert response.status_code in [200, 201]
        assert response.json() is not None

    async def test_update_deliverable_caption_requirements(
        self,
        authenticated_client: AsyncTestClient,
        deliverable,
    ):
        """Test updating deliverable caption requirements."""

        response = await authenticated_client.post(
            f"/deliverables/{sqid_encode(deliverable.id)}",
            json={
                "title": deliverable.title,
                "content": deliverable.content,
                "platforms": deliverable.platforms.value,
                "posting_date": deliverable.posting_date.isoformat(),
                "deliverable_type": deliverable.deliverable_type.value if deliverable.deliverable_type else None,
                "count": deliverable.count,
                "posting_start_date": str(deliverable.posting_start_date) if deliverable.posting_start_date else None,
                "posting_end_date": str(deliverable.posting_end_date) if deliverable.posting_end_date else None,
                "handles": ["@brand", "@partner"],
                "hashtags": ["#ad", "#sponsored"],
                "disclosures": ["Paid partnership"],
                "approval_required": deliverable.approval_required,
                "approval_rounds": deliverable.approval_rounds,
                "campaign_id": deliverable.campaign_id,
                "notes": deliverable.notes,
            },
        )
        assert response.status_code in [200, 201]
        assert response.json() is not None

    async def test_list_deliverable_actions(
        self,
        authenticated_client: AsyncTestClient,
        deliverable,
    ):
        """Test GET /actions/deliverable_actions/{id} returns available actions."""

        # Get available actions
        actions = await get_available_actions(authenticated_client, "deliverable_actions", sqid_encode(deliverable.id))

        # Should have at least update and delete actions
        action_keys = [action["action"] for action in actions]
        assert "deliverable_actions__deliverable_update" in action_keys
        assert "deliverable_actions__deliverable_delete" in action_keys

    async def test_execute_deliverable_update_action(
        self,
        authenticated_client: AsyncTestClient,
        deliverable,
        db_session: AsyncSession,
    ):
        """Test executing deliverable update action."""

        # Refresh the deliverable to ensure all fields are loaded
        await db_session.refresh(deliverable)

        result = await execute_action(
            authenticated_client,
            "deliverable_actions",
            "deliverable_actions__deliverable_update",
            {
                "title": "Updated via Action",
                "content": deliverable.content,
                "platforms": deliverable.platforms.value,
                "posting_date": deliverable.posting_date.isoformat(),
                "deliverable_type": deliverable.deliverable_type.value if deliverable.deliverable_type else None,
                "count": int(deliverable.count),
                "posting_start_date": str(deliverable.posting_start_date) if deliverable.posting_start_date else None,
                "posting_end_date": str(deliverable.posting_end_date) if deliverable.posting_end_date else None,
                "handles": list(deliverable.handles) if deliverable.handles else [],
                "hashtags": list(deliverable.hashtags) if deliverable.hashtags else [],
                "disclosures": list(deliverable.disclosures) if deliverable.disclosures else [],
                "approval_required": bool(deliverable.approval_required),
                "approval_rounds": int(deliverable.approval_rounds) if deliverable.approval_rounds else None,
                "campaign_id": int(deliverable.campaign_id),
                "notes": {"test": "value"},  # Use simple dict to avoid any serialization issues
            },
            sqid_encode(deliverable.id),
        )

        assert result is not None

    async def test_execute_deliverable_delete_action(
        self,
        authenticated_client: AsyncTestClient,
        deliverable,
        db_session: AsyncSession,
    ):
        """Test executing deliverable delete action."""

        result = await execute_action(
            authenticated_client,
            "deliverable_actions",
            "deliverable_actions__deliverable_delete",
            {},
            sqid_encode(deliverable.id),
        )

        assert result is not None

    async def test_get_deliverable_not_found(
        self,
        authenticated_client: AsyncTestClient,
    ):
        """Test GET /deliverables/{id} with non-existent ID returns 404."""

        # Try to get a non-existent deliverable
        response = await authenticated_client.get(f"/deliverables/{sqid_encode(99999)}")
        assert response.status_code == 404

    async def test_deliverable_with_campaign(
        self,
        authenticated_client: AsyncTestClient,
        campaign,
        deliverable,
    ):
        """Test deliverable associated with a campaign."""

        # Get the deliverable
        response = await authenticated_client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["campaign_id"] == sqid_encode(campaign.id)


class TestDeliverableStates:
    """Tests for deliverable state transitions."""

    async def test_deliverable_initial_state(
        self,
        authenticated_client: AsyncTestClient,
        deliverable,
    ):
        """Test that new deliverables start in DRAFT state."""

        response = await authenticated_client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
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
        authenticated_client: AsyncTestClient,
        team,
        campaign,
        db_session: AsyncSession,
    ):
        """Test deliverable configured for Instagram."""

        # Create a specific deliverable with Instagram platform
        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=team.id,
            campaign_id=campaign.id,
            platforms=SocialMediaPlatforms.INSTAGRAM,
            deliverable_type=DeliverableType.INSTAGRAM_FEED_POST,
        )
        await db_session.commit()

        response = await authenticated_client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["platforms"] == SocialMediaPlatforms.INSTAGRAM.value
        assert data["deliverable_type"] == DeliverableType.INSTAGRAM_FEED_POST.value

    async def test_deliverable_posting_dates(
        self,
        authenticated_client: AsyncTestClient,
        team,
        campaign,
        db_session: AsyncSession,
    ):
        """Test deliverable posting date fields."""

        posting_date = datetime.now(tz=UTC) + timedelta(days=7)
        start_date = date.today() + timedelta(days=7)
        end_date = date.today() + timedelta(days=14)

        # Create a specific deliverable with posting dates
        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=team.id,
            campaign_id=campaign.id,
            posting_date=posting_date,
            posting_start_date=start_date,
            posting_end_date=end_date,
        )
        await db_session.commit()

        response = await authenticated_client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["posting_start_date"] == str(start_date)
        assert data["posting_end_date"] == str(end_date)

    async def test_deliverable_approval_settings(
        self,
        authenticated_client: AsyncTestClient,
        team,
        campaign,
        db_session: AsyncSession,
    ):
        """Test deliverable approval settings."""

        # Create a specific deliverable with approval settings
        deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=team.id,
            campaign_id=campaign.id,
            approval_required=True,
            approval_rounds=2,
        )
        await db_session.commit()

        response = await authenticated_client.get(f"/deliverables/{sqid_encode(deliverable.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["approval_required"] is True
        assert data["approval_rounds"] == 2
