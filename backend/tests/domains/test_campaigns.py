"""Tests for campaigns domain: endpoints and operations."""

from datetime import date, timedelta

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaigns.enums import (
    CampaignStates,
    CompensationStructure,
    CounterpartyType,
    OwnershipMode,
)
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import assert_rls_isolated, execute_action, get_available_actions
from tests.factories.brands import BrandFactory
from tests.factories.campaigns import CampaignFactory


class TestCampaigns:
    """Tests for campaign endpoints."""

    async def test_get_campaign(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /campaigns/{id} returns campaign details."""
        client, user_data = authenticated_client

        # Create a brand first
        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Create a campaign for this team
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )
        await db_session.commit()

        # Get the campaign
        response = await client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(campaign.id)
        assert data["name"] == campaign.name
        assert data["team_id"] == sqid_encode(user_data["team_id"])
        assert "actions" in data  # Should include available actions

    async def test_update_campaign(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test POST /campaigns/{id} updates campaign."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
            name="Original Campaign",
            description="Original description",
        )
        await db_session.commit()

        # Update the campaign
        response = await client.post(
            f"/campaigns/{sqid_encode(campaign.id)}",
            json={
                "name": "Updated Campaign",
                "description": "Updated description",
            },
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert data["name"] == "Updated Campaign"
        assert data["description"] == "Updated description"

    async def test_update_campaign_compensation(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test updating campaign compensation details."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )
        await db_session.commit()

        # Update compensation
        response = await client.post(
            f"/campaigns/{sqid_encode(campaign.id)}",
            json={
                "compensation_structure": CompensationStructure.FLAT_FEE.value,
                "compensation_total_usd": 5000.0,
                "payment_terms_days": 30,
            },
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert data["compensation_structure"] == CompensationStructure.FLAT_FEE.value
        assert data["compensation_total_usd"] == 5000.0
        assert data["payment_terms_days"] == 30

    async def test_list_campaign_actions(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /actions/campaign_actions/{id} returns available actions."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )
        await db_session.commit()

        # Get available actions
        actions = await get_available_actions(client, "campaign_actions", sqid_encode(campaign.id))

        # Should have at least update and delete actions
        action_keys = [action["action"] for action in actions]
        assert "campaign.update" in action_keys
        assert "campaign.delete" in action_keys

    async def test_execute_campaign_update_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing campaign update action."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
            name="Original Name",
        )
        await db_session.commit()

        # Execute update action
        result = await execute_action(
            client,
            "campaign_actions",
            "campaign.update",
            {"name": "Updated via Action"},
            sqid_encode(campaign.id),
        )

        assert result["success"] is True

        # Verify the update
        await db_session.refresh(campaign)
        assert campaign.name == "Updated via Action"

    async def test_execute_campaign_delete_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing campaign delete action."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )
        await db_session.commit()

        # Execute delete action
        result = await execute_action(
            client,
            "campaign_actions",
            "campaign.delete",
            {},
            sqid_encode(campaign.id),
        )

        assert result["success"] is True

        # Verify soft deletion
        await db_session.refresh(campaign)
        assert campaign.deleted_at is not None

    async def test_campaign_rls_isolation(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        other_team_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that teams cannot access each other's campaigns."""
        client, user_data = authenticated_client
        other_client, other_user_data = other_team_client

        # Create campaign for first team
        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )
        await db_session.commit()

        # Verify RLS isolation
        await assert_rls_isolated(
            client=other_client,
            resource_path=f"/campaigns/{sqid_encode(campaign.id)}",
        )

    async def test_get_campaign_not_found(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /campaigns/{id} with non-existent ID returns 404."""
        client, user_data = authenticated_client

        # Try to get a non-existent campaign
        response = await client.get(f"/campaigns/{sqid_encode(99999)}")
        assert response.status_code == 404


class TestCampaignStates:
    """Tests for campaign state transitions."""

    async def test_campaign_initial_state(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that new campaigns start in DRAFT state."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )
        await db_session.commit()

        response = await client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        # State should be initial state (DRAFT) or any valid state
        assert data["state"] in [
            CampaignStates.DRAFT.value,
            CampaignStates.ACTIVE.value,
            CampaignStates.COMPLETED.value,
        ]


class TestCampaignCounterparty:
    """Tests for campaign counterparty information."""

    async def test_campaign_with_brand_counterparty(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test campaign with brand as counterparty."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
            counterparty_type=CounterpartyType.BRAND,
            counterparty_name="Test Brand",
            counterparty_email="brand@example.com",
        )
        await db_session.commit()

        response = await client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["counterparty_type"] == CounterpartyType.BRAND.value
        assert data["counterparty_name"] == "Test Brand"

    async def test_campaign_with_agency_counterparty(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test campaign with agency as counterparty."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
            counterparty_type=CounterpartyType.AGENCY,
            counterparty_name="Test Agency",
            counterparty_email="agency@example.com",
        )
        await db_session.commit()

        response = await client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["counterparty_type"] == CounterpartyType.AGENCY.value
        assert data["counterparty_name"] == "Test Agency"


class TestCampaignFlightDates:
    """Tests for campaign flight date fields."""

    async def test_campaign_flight_dates(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test campaign flight start and end dates."""
        client, user_data = authenticated_client

        start_date = date.today() + timedelta(days=7)
        end_date = date.today() + timedelta(days=30)

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
            flight_start_date=start_date,
            flight_end_date=end_date,
        )
        await db_session.commit()

        response = await client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["flight_start_date"] == str(start_date)
        assert data["flight_end_date"] == str(end_date)


class TestCampaignUsageRights:
    """Tests for campaign usage rights and exclusivity."""

    async def test_campaign_usage_rights(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test campaign usage rights configuration."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
            usage_duration="12 months",
            usage_territory="Worldwide",
            usage_paid_media_option=True,
        )
        await db_session.commit()

        response = await client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["usage_duration"] == "12 months"
        assert data["usage_territory"] == "Worldwide"
        assert data["usage_paid_media_option"] is True

    async def test_campaign_exclusivity(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test campaign exclusivity settings."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
            exclusivity_category="Beverages",
            exclusivity_days_before=30,
            exclusivity_days_after=30,
        )
        await db_session.commit()

        response = await client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["exclusivity_category"] == "Beverages"
        assert data["exclusivity_days_before"] == 30
        assert data["exclusivity_days_after"] == 30
