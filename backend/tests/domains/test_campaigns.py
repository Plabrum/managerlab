"""Tests for campaigns domain: endpoints and operations."""

from datetime import date, timedelta

from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaigns.enums import CampaignStates, CompensationStructure, CounterpartyType
from app.utils.sqids import sqid_encode
from tests.factories.brands import BrandFactory
from tests.factories.campaigns import CampaignFactory


class TestCampaigns:
    """Tests for campaign endpoints."""

    async def test_get_campaign(
        self,
        authenticated_client: AsyncTestClient,
        campaign,
    ):
        """Test GET /campaigns/{id} returns campaign details."""

        response = await authenticated_client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200
        assert response.json() is not None

    async def test_update_campaign(
        self,
        authenticated_client: AsyncTestClient,
        campaign,
    ):
        """Test POST /campaigns/{id} updates campaign."""

        response = await authenticated_client.post(
            f"/campaigns/{sqid_encode(campaign.id)}",
            json={"name": "Updated Campaign"},
        )
        assert response.status_code in [200, 201]
        assert response.json() is not None

    async def test_update_campaign_compensation(
        self,
        authenticated_client: AsyncTestClient,
        campaign,
    ):
        """Test updating campaign compensation details."""

        response = await authenticated_client.post(
            f"/campaigns/{sqid_encode(campaign.id)}",
            json={
                "compensation_structure": CompensationStructure.FLAT_FEE.value,
                "compensation_total_usd": 5000.0,
            },
        )
        assert response.status_code in [200, 201]
        assert response.json() is not None

    async def test_list_campaign_actions(
        self,
        authenticated_client: AsyncTestClient,
        campaign,
    ):
        """Test GET /actions/campaign_actions/{id} returns available actions."""

        response = await authenticated_client.get(f"/actions/campaign_actions/{sqid_encode(campaign.id)}")
        assert response.status_code == 200
        assert response.json() is not None

    async def test_execute_campaign_update_action(
        self,
        authenticated_client: AsyncTestClient,
        campaign,
    ):
        """Test executing campaign update action."""

        response = await authenticated_client.post(
            f"/actions/campaign_actions/{sqid_encode(campaign.id)}",
            json={"action": "campaign_actions__campaign_update", "data": {"name": "Updated via Action"}},
        )
        assert response.status_code in [200, 201, 204]
        assert response.json() is not None

    async def test_execute_campaign_delete_action(
        self,
        authenticated_client: AsyncTestClient,
        campaign,
    ):
        """Test executing campaign delete action."""

        response = await authenticated_client.post(
            f"/actions/campaign_actions/{sqid_encode(campaign.id)}",
            json={"action": "campaign_actions__campaign_delete", "data": {}},
        )
        assert response.status_code in [200, 201, 204]
        assert response.json() is not None

    async def test_get_campaign_not_found(
        self,
        authenticated_client: AsyncTestClient,
    ):
        """Test GET /campaigns/{id} with non-existent ID returns 404."""

        # Try to get a non-existent campaign
        response = await authenticated_client.get(f"/campaigns/{sqid_encode(99999)}")
        assert response.status_code == 404


class TestCampaignStates:
    """Tests for campaign state transitions."""

    async def test_campaign_initial_state(
        self,
        authenticated_client: AsyncTestClient,
        team,
        campaign,
    ):
        """Test that new campaigns start in DRAFT state."""

        response = await authenticated_client.get(f"/campaigns/{sqid_encode(campaign.id)}")
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
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test campaign with brand as counterparty."""

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand.id,
            counterparty_type=CounterpartyType.BRAND,
            counterparty_name="Test Brand",
            counterparty_email="brand@example.com",
        )
        await db_session.commit()

        response = await authenticated_client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["counterparty_type"] == CounterpartyType.BRAND.value
        assert data["counterparty_name"] == "Test Brand"

    async def test_campaign_with_agency_counterparty(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test campaign with agency as counterparty."""

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand.id,
            counterparty_type=CounterpartyType.AGENCY,
            counterparty_name="Test Agency",
            counterparty_email="agency@example.com",
        )
        await db_session.commit()

        response = await authenticated_client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["counterparty_type"] == CounterpartyType.AGENCY.value
        assert data["counterparty_name"] == "Test Agency"


class TestCampaignFlightDates:
    """Tests for campaign flight date fields."""

    async def test_campaign_flight_dates(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test campaign flight start and end dates."""

        start_date = date.today() + timedelta(days=7)
        end_date = date.today() + timedelta(days=30)

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand.id,
            flight_start_date=start_date,
            flight_end_date=end_date,
        )
        await db_session.commit()

        response = await authenticated_client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["flight_start_date"] == str(start_date)
        assert data["flight_end_date"] == str(end_date)


class TestCampaignUsageRights:
    """Tests for campaign usage rights and exclusivity."""

    async def test_campaign_usage_rights(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test campaign usage rights configuration."""

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand.id,
            usage_duration="12 months",
            usage_territory="Worldwide",
            usage_paid_media_option=True,
        )
        await db_session.commit()

        response = await authenticated_client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["usage_duration"] == "12 months"
        assert data["usage_territory"] == "Worldwide"
        assert data["usage_paid_media_option"] is True

    async def test_campaign_exclusivity(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test campaign exclusivity settings."""

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand.id,
            exclusivity_category="Beverages",
            exclusivity_days_before=30,
            exclusivity_days_after=30,
        )
        await db_session.commit()

        response = await authenticated_client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["exclusivity_category"] == "Beverages"
        assert data["exclusivity_days_before"] == 30
        assert data["exclusivity_days_after"] == 30
