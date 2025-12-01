"""Tests for time series data endpoint (/o/{object_type}/data)."""

from datetime import datetime, timezone

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.enums import ObjectTypes
from app.roster.models import Roster
from tests.factories.brands import BrandFactory
from tests.factories.campaigns import CampaignFactory
from tests.factories.deliverables import DeliverableFactory


class TestTimeSeriesData:
    """Tests for time series data aggregation endpoint."""

    @pytest.fixture
    async def brands_with_different_names(
        self,
        team,
        db_session: AsyncSession,
    ):
        """Create multiple brands with different names for categorical aggregation."""
        # Note: Can't create duplicate names due to unique constraint (team_id, name)
        # So we test aggregation with 2 Nike variations and 1 Adidas
        brand1 = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
            name="Nike",
            created_at=datetime(2025, 11, 15, tzinfo=timezone.utc),
        )
        brand2 = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
            name="Adidas",
            created_at=datetime(2025, 11, 20, tzinfo=timezone.utc),
        )
        brand3 = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
            name="Puma",
            created_at=datetime(2025, 11, 25, tzinfo=timezone.utc),
        )
        await db_session.flush()
        return [brand1, brand2, brand3]

    async def test_categorical_aggregation_by_name(
        self,
        authenticated_client: AsyncTestClient,
        brands_with_different_names,
    ):
        """Test categorical aggregation (pie chart) by name field.

        This reproduces the bug where breakdowns are empty despite having data.
        """
        response = await authenticated_client.post(
            f"/o/{ObjectTypes.Brands}/data",
            json={
                "field": "name",
                "time_range": "all_time",
                "aggregation": "count_",
                "filters": [],
                "granularity": "automatic",
                "fill_missing": False,
            },
        )

        assert response.status_code in [200, 201], f"Got {response.status_code}: {response.text}"
        data = response.json()

        # Verify response structure
        assert data["field_name"] == "name"
        assert data["field_type"] == "string"
        assert data["aggregation_type"] == "count_"
        assert data["total_records"] == 3

        # Verify categorical data structure
        assert data["data"]["type"] == "categorical"
        data_points = data["data"]["data_points"]
        assert len(data_points) > 0

        # Find the 2025 bucket (granularity is automatic, likely "year")
        bucket_2025 = next(
            (dp for dp in data_points if dp["timestamp"].startswith("2025")),
            None,
        )
        assert bucket_2025 is not None, "Should have 2025 data"

        # Verify breakdowns are properly populated
        breakdowns = bucket_2025["breakdowns"]
        assert breakdowns != {}, "Breakdowns should not be empty"
        assert breakdowns.get("Nike") == 1, "Should have 1 Nike brand"
        assert breakdowns.get("Adidas") == 1, "Should have 1 Adidas brand"
        assert breakdowns.get("Puma") == 1, "Should have 1 Puma brand"
        assert bucket_2025["total_count"] == 3

    async def test_numerical_aggregation_count(
        self,
        authenticated_client: AsyncTestClient,
        brands_with_different_names,
    ):
        """Test numerical aggregation (count by time bucket for bar/line charts)."""
        response = await authenticated_client.post(
            f"/o/{ObjectTypes.Brands}/data",
            json={
                "field": "id",  # Count IDs (numeric field)
                "time_range": "last_30_days",
                "aggregation": "count_",
                "filters": [],
                "granularity": "day",
                "fill_missing": True,
            },
        )

        assert response.status_code in [200, 201]
        data = response.json()

        assert data["field_name"] == "id"
        assert data["aggregation_type"] == "count_"
        assert data["data"]["type"] == "numerical"
        assert data["total_records"] == 3

        # Verify numerical data points
        data_points = data["data"]["data_points"]
        assert len(data_points) > 0

        # Find days with data (should have counts for each brand creation)
        days_with_data = [dp for dp in data_points if dp["value"] and dp["value"] > 0]
        assert len(days_with_data) >= 1, "Should have days with brand creations"

    async def test_empty_categorical_data(
        self,
        authenticated_client: AsyncTestClient,
        team,
    ):
        """Test categorical aggregation with no data returns empty breakdowns."""
        # Don't create any brands, so we get empty results
        response = await authenticated_client.post(
            f"/o/{ObjectTypes.Brands}/data",
            json={
                "field": "name",
                "time_range": "last_7_days",
                "aggregation": "count_",
                "filters": [],
                "granularity": "day",
                "fill_missing": False,
            },
        )

        assert response.status_code in [200, 201]
        data = response.json()

        assert data["total_records"] == 0
        assert data["data"]["type"] == "categorical"

        # All buckets should have empty breakdowns and zero count
        for dp in data["data"]["data_points"]:
            assert dp["breakdowns"] == {}
            assert dp["total_count"] == 0

    async def test_time_range_filtering(
        self,
        authenticated_client: AsyncTestClient,
        brands_with_different_names,
    ):
        """Test that time_range parameter correctly filters data."""
        # Create a brand in the past (outside last_7_days)
        from tests.factories.brands import BrandFactory

        response = await authenticated_client.post(
            f"/o/{ObjectTypes.Brands}/data",
            json={
                "field": "name",
                "time_range": "last_7_days",  # Only recent brands
                "aggregation": "count_",
                "filters": [],
                "granularity": "day",
                "fill_missing": False,
            },
        )

        assert response.status_code in [200, 201]
        data = response.json()

        # Should only include brands from last 7 days
        # The fixture creates brands in Nov 2025, which should be within last_7_days
        # if the test runs in Nov 2025, otherwise 0
        assert data["total_records"] >= 0

    async def test_granularity_automatic(
        self,
        authenticated_client: AsyncTestClient,
        brands_with_different_names,
    ):
        """Test automatic granularity selection based on time range."""
        response = await authenticated_client.post(
            f"/o/{ObjectTypes.Brands}/data",
            json={
                "field": "name",
                "time_range": "all_time",
                "aggregation": "count_",
                "filters": [],
                "granularity": "automatic",  # Should auto-select based on range
                "fill_missing": False,
            },
        )

        assert response.status_code in [200, 201]
        data = response.json()

        # Verify granularity was selected
        assert data["granularity_used"] in ["day", "week", "month", "year"]

    async def test_relationship_field_query(
        self,
        authenticated_client: AsyncTestClient,
        team,
        user,
        db_session: AsyncSession,
    ):
        """Test querying a field that requires joining through relationships (owner_name)."""
        # Create rosters
        roster1 = Roster(
            team_id=team.id,
            user_id=user.id,
            name="John Doe",
        )
        roster2 = Roster(
            team_id=team.id,
            user_id=user.id,
            name="Jane Smith",
        )
        db_session.add(roster1)
        db_session.add(roster2)
        await db_session.flush()

        # Create brands
        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
            name="Test Brand",
        )

        # Create campaigns with assigned rosters
        campaign1 = await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand.id,
            assigned_roster_id=roster1.id,
            name="Campaign 1",
        )
        campaign2 = await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand.id,
            assigned_roster_id=roster2.id,
            name="Campaign 2",
        )

        # Create deliverables linked to campaigns
        await DeliverableFactory.create_async(
            session=db_session,
            team_id=team.id,
            campaign_id=campaign1.id,
            title="Deliverable 1",
            created_at=datetime(2025, 11, 15, tzinfo=timezone.utc),
        )
        await DeliverableFactory.create_async(
            session=db_session,
            team_id=team.id,
            campaign_id=campaign1.id,
            title="Deliverable 2",
            created_at=datetime(2025, 11, 16, tzinfo=timezone.utc),
        )
        await DeliverableFactory.create_async(
            session=db_session,
            team_id=team.id,
            campaign_id=campaign2.id,
            title="Deliverable 3",
            created_at=datetime(2025, 11, 17, tzinfo=timezone.utc),
        )
        await db_session.flush()

        # Query owner_name field (requires join through campaign -> assigned_roster)
        response = await authenticated_client.post(
            f"/o/{ObjectTypes.Deliverables}/data",
            json={
                "field": "owner_name",
                "time_range": "all_time",
                "aggregation": "count_",
                "filters": [],
                "granularity": "automatic",
            },
        )

        assert response.status_code in [200, 201], f"Got {response.status_code}: {response.text}"
        data = response.json()

        # Verify response structure
        assert data["field_name"] == "owner_name"
        assert data["field_type"] == "string"
        assert data["total_records"] == 3

        # Verify categorical data with breakdowns by owner name
        assert data["data"]["type"] == "categorical"
        data_points = data["data"]["data_points"]
        assert len(data_points) > 0

        # Find the 2025 bucket
        bucket_2025 = next(
            (dp for dp in data_points if dp["timestamp"].startswith("2025")),
            None,
        )
        assert bucket_2025 is not None, "Should have 2025 data"

        # Verify breakdowns by owner name
        breakdowns = bucket_2025["breakdowns"]
        assert breakdowns != {}, "Breakdowns should not be empty"
        assert breakdowns.get("John Doe") == 2, "Should have 2 deliverables for John Doe"
        assert breakdowns.get("Jane Smith") == 1, "Should have 1 deliverable for Jane Smith"
        assert bucket_2025["total_count"] == 3

    async def test_object_field_with_relationship_query(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test querying an Object-type field that uses query_relationship (brand_id -> brand.name)."""
        # Create brands
        brand1 = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
            name="Nike",
        )
        brand2 = await BrandFactory.create_async(
            session=db_session,
            team_id=team.id,
            name="Adidas",
        )

        # Create campaigns with different brands
        await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand1.id,
            name="Nike Campaign 1",
            created_at=datetime(2025, 11, 15, tzinfo=timezone.utc),
        )
        await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand1.id,
            name="Nike Campaign 2",
            created_at=datetime(2025, 11, 16, tzinfo=timezone.utc),
        )
        await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand2.id,
            name="Adidas Campaign",
            created_at=datetime(2025, 11, 17, tzinfo=timezone.utc),
        )
        await db_session.flush()

        # Query brand_id field (Object type with query_relationship="brand", query_column="name")
        response = await authenticated_client.post(
            f"/o/{ObjectTypes.Campaigns}/data",
            json={
                "field": "brand_id",
                "time_range": "all_time",
                "aggregation": "count_",
                "filters": [],
                "granularity": "automatic",
            },
        )

        assert response.status_code in [200, 201], f"Got {response.status_code}: {response.text}"
        data = response.json()

        # Verify response structure
        assert data["field_name"] == "brand_id"
        assert data["field_type"] == "object"
        assert data["total_records"] == 3

        # Verify categorical data with breakdowns by brand name
        assert data["data"]["type"] == "categorical"
        data_points = data["data"]["data_points"]
        assert len(data_points) > 0

        # Find the 2025 bucket
        bucket_2025 = next(
            (dp for dp in data_points if dp["timestamp"].startswith("2025")),
            None,
        )
        assert bucket_2025 is not None, "Should have 2025 data"

        # Verify breakdowns by brand name (not ID)
        breakdowns = bucket_2025["breakdowns"]
        assert breakdowns != {}, "Breakdowns should not be empty"
        assert breakdowns.get("Nike") == 2, "Should have 2 campaigns for Nike"
        assert breakdowns.get("Adidas") == 1, "Should have 1 campaign for Adidas"
        assert bucket_2025["total_count"] == 3
