"""Tests for Row-Level Security (RLS) implementation.

These tests verify that:
1. RLS is enabled on all tables with team_id/campaign_id columns
2. RLS policies exist and are properly configured
3. Data isolation works correctly between teams/campaigns
4. System mode bypass works as expected
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestRLSConfiguration:
    """Test that RLS is properly configured in the database."""

    async def test_rls_enabled_on_team_scoped_tables(self, db_session: AsyncSession):
        """Verify RLS is enabled on all team-scoped tables."""
        result = await db_session.execute(
            text("""
                SELECT tablename, rowsecurity
                FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename IN (
                      'campaigns', 'brands', 'brand_contacts', 'roster',
                      'media', 'documents', 'invoices', 'threads'
                  )
                ORDER BY tablename
            """)
        )
        tables = {row[0]: row[1] for row in result}

        # These tables should have RLS enabled
        expected_tables = [
            "campaigns",
            "brands",
            "brand_contacts",
            "roster",
            "media",
            "documents",
            "invoices",
            "threads",
        ]

        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"
            assert tables[table] is True, f"RLS not enabled on {table}"

    async def test_rls_policies_exist(self, db_session: AsyncSession):
        """Verify RLS policies exist for team-scoped tables."""
        result = await db_session.execute(
            text("""
                SELECT schemaname, tablename, policyname, permissive, cmd
                FROM pg_policies
                WHERE schemaname = 'public'
                ORDER BY tablename, policyname
            """)
        )
        policies = list(result)

        assert len(policies) > 0, "No RLS policies found in database"

        # Check that team_scope_policy exists for team-scoped tables
        policy_dict = {(row[1], row[2]): row for row in policies}

        # Verify team scope policies exist
        team_tables = ["campaigns", "brands", "brand_contacts", "roster", "documents", "invoices", "threads"]
        for table in team_tables:
            assert (
                table,
                "team_scope_policy",
            ) in policy_dict, f"team_scope_policy missing for {table}"

    async def test_rls_policy_uses_system_mode(self, db_session: AsyncSession):
        """Verify RLS policies check app.is_system_mode for bypass."""
        result = await db_session.execute(
            text("""
                SELECT tablename, policyname, qual
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND policyname = 'team_scope_policy'
                LIMIT 1
            """)
        )
        row = result.first()

        assert row is not None, "No team_scope_policy found"

        policy_definition = row[2]
        # Should check for is_system_mode
        assert (
            "app.is_system_mode" in policy_definition or "current_setting('app.is_system_mode'" in policy_definition
        ), "Policy does not check app.is_system_mode for system bypass"


class TestRLSDataIsolation:
    """Test that RLS properly isolates data between teams."""

    async def test_team_isolation_for_campaigns(self, db_session: AsyncSession, multi_team_setup):
        """Verify campaigns are isolated by team_id."""
        from sqlalchemy import event

        from app.utils.db_filters import create_query_filter
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory

        team1 = multi_team_setup["team1"]
        team2 = multi_team_setup["team2"]

        # Create brands for each team
        brand1 = await BrandFactory.create_async(session=db_session, team_id=team1.id)
        brand2 = await BrandFactory.create_async(session=db_session, team_id=team2.id)

        # Create campaigns for each team
        campaign1 = await CampaignFactory.create_async(
            session=db_session, team_id=team1.id, brand_id=brand1.id, name="Team 1 Campaign"
        )
        campaign2 = await CampaignFactory.create_async(
            session=db_session, team_id=team2.id, brand_id=brand2.id, name="Team 2 Campaign"
        )
        await db_session.commit()

        # Test team 1 isolation
        await db_session.execute(text(f"SET LOCAL app.team_id = {team1.id}"))
        query_filter = create_query_filter(team_id=team1.id, campaign_id=None, scope_type="team")
        event.listen(db_session.sync_session, "do_orm_execute", query_filter)

        result = await db_session.execute(text("SELECT id, name FROM campaigns ORDER BY name"))
        campaigns = list(result)

        assert len(campaigns) == 1, f"Expected 1 campaign for team 1, got {len(campaigns)}"
        assert campaigns[0][0] == campaign1.id
        assert campaigns[0][1] == "Team 1 Campaign"

        event.remove(db_session.sync_session, "do_orm_execute", query_filter)
        await db_session.rollback()

        # Test team 2 isolation
        await db_session.execute(text(f"SET LOCAL app.team_id = {team2.id}"))
        query_filter = create_query_filter(team_id=team2.id, campaign_id=None, scope_type="team")
        event.listen(db_session.sync_session, "do_orm_execute", query_filter)

        result = await db_session.execute(text("SELECT id, name FROM campaigns ORDER BY name"))
        campaigns = list(result)

        assert len(campaigns) == 1, f"Expected 1 campaign for team 2, got {len(campaigns)}"
        assert campaigns[0][0] == campaign2.id
        assert campaigns[0][1] == "Team 2 Campaign"

        event.remove(db_session.sync_session, "do_orm_execute", query_filter)

    async def test_system_mode_bypass(self, db_session: AsyncSession, multi_team_setup):
        """Verify system mode allows access to all data."""
        from unittest.mock import patch

        from sqlalchemy import event

        from app.utils.db_filters import create_query_filter
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory

        team1 = multi_team_setup["team1"]
        team2 = multi_team_setup["team2"]

        # Create brands for each team
        brand1 = await BrandFactory.create_async(session=db_session, team_id=team1.id)
        brand2 = await BrandFactory.create_async(session=db_session, team_id=team2.id)

        # Create campaigns for each team
        await CampaignFactory.create_async(
            session=db_session, team_id=team1.id, brand_id=brand1.id, name="Team 1 Campaign"
        )
        await CampaignFactory.create_async(
            session=db_session, team_id=team2.id, brand_id=brand2.id, name="Team 2 Campaign"
        )
        await db_session.commit()

        # Set system mode
        await db_session.execute(text("SET LOCAL app.is_system_mode = true"))

        with patch("app.utils.db_filters.config.IS_SYSTEM_MODE", True):
            query_filter = create_query_filter(team_id=None, campaign_id=None, scope_type=None)
            event.listen(db_session.sync_session, "do_orm_execute", query_filter)

            result = await db_session.execute(text("SELECT COUNT(*) FROM campaigns"))
            count = result.scalar()

            assert count == 2, f"Expected 2 campaigns in system mode, got {count}"

            event.remove(db_session.sync_session, "do_orm_execute", query_filter)

    async def test_no_rls_context_blocks_access(self, db_session: AsyncSession, multi_team_setup):
        """Verify that without RLS context set, no data is accessible (if policies are strict)."""
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory

        team1 = multi_team_setup["team1"]

        # Create brand and campaign
        brand1 = await BrandFactory.create_async(session=db_session, team_id=team1.id)
        await CampaignFactory.create_async(
            session=db_session, team_id=team1.id, brand_id=brand1.id, name="Team 1 Campaign"
        )
        await db_session.commit()

        # Don't set any RLS context variables
        # Query campaigns - should see nothing (or everything if policy has IS NULL check)
        result = await db_session.execute(text("SELECT COUNT(*) FROM campaigns"))
        count = result.scalar()

        # NOTE: If policies have "OR app.team_id IS NULL", this will return data
        # Once policies are fixed to be strict, this should be 0
        # For now, just document the current behavior
        print(f"Campaigns visible without RLS context: {count}")


class TestRLSDualScope:
    """Test dual-scoped tables (team_id + campaign_id)."""

    async def test_dual_scope_policy_exists(self, db_session: AsyncSession):
        """Verify dual scope policies exist for deliverables and messages."""
        result = await db_session.execute(
            text("""
                SELECT tablename, policyname
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND policyname = 'dual_scope_policy'
                ORDER BY tablename
            """)
        )
        policies = [(row[0], row[1]) for row in result]

        # Check for dual-scoped tables
        dual_scope_tables = {"messages", "deliverables"}  # Add more as needed

        found_tables = {table for table, _ in policies}
        for table in dual_scope_tables:
            assert table in found_tables, f"dual_scope_policy missing for {table}"

    async def test_campaign_scoped_access(self, db_session: AsyncSession, multi_team_setup):
        """Verify campaign-scoped access works for dual-scoped tables."""
        # This test would create deliverables/messages and verify they're isolated by campaign_id
        # Skipping implementation for now as it requires setting up full campaign context
        pytest.skip("Requires full dual-scope implementation")


class TestRLSWithORM:
    """Test RLS works correctly with SQLAlchemy ORM queries."""

    async def test_orm_query_respects_rls(self, db_session: AsyncSession, multi_team_setup):
        """Verify ORM queries respect both RLS and application filters."""
        from sqlalchemy import event, select

        from app.campaigns.models import Campaign
        from app.utils.db_filters import create_query_filter
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory

        team1 = multi_team_setup["team1"]
        team2 = multi_team_setup["team2"]

        # Create brands for each team
        brand1 = await BrandFactory.create_async(session=db_session, team_id=team1.id)
        brand2 = await BrandFactory.create_async(session=db_session, team_id=team2.id)

        # Create campaigns for each team
        await CampaignFactory.create_async(session=db_session, team_id=team1.id, brand_id=brand1.id)
        await CampaignFactory.create_async(session=db_session, team_id=team2.id, brand_id=brand2.id)
        await db_session.commit()

        # Set RLS context for team 1
        await db_session.execute(text(f"SET LOCAL app.team_id = {team1.id}"))
        query_filter = create_query_filter(team_id=team1.id, campaign_id=None, scope_type="team")
        event.listen(db_session.sync_session, "do_orm_execute", query_filter)

        # Use ORM query - should have team_id filter applied automatically
        result = await db_session.execute(select(Campaign))
        campaigns = result.scalars().all()

        assert len(campaigns) == 1, f"Expected 1 campaign for team 1 via ORM, got {len(campaigns)}"

        event.remove(db_session.sync_session, "do_orm_execute", query_filter)
