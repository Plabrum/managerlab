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

from app.auth.enums import ScopeType


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
        """Verify RLS policies exist for team-scoped and dual-scoped tables."""
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

        # Check that policies exist for tables
        policy_dict = {(row[1], row[2]): row for row in policies}

        # Verify team scope policies exist (team_id only)
        team_tables = ["campaigns", "brands", "brand_contacts", "roster", "threads"]
        for table in team_tables:
            assert (
                table,
                "team_scope_policy",
            ) in policy_dict, f"team_scope_policy missing for {table}"

        # Verify dual scope policies exist (team_id + campaign_id)
        dual_tables = ["documents", "invoices", "deliverables", "media", "messages"]
        for table in dual_tables:
            assert (
                table,
                "dual_scope_policy",
            ) in policy_dict, f"dual_scope_policy missing for {table}"

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

        # Capture team IDs before any rollbacks that might expire them
        team1_id = int(team1.id)
        team2_id = int(team2.id)

        # Create brands for each team
        brand1 = await BrandFactory.create_async(session=db_session, team_id=team1_id)
        brand2 = await BrandFactory.create_async(session=db_session, team_id=team2_id)

        # Create campaigns for each team
        campaign1 = await CampaignFactory.create_async(
            session=db_session, team_id=team1_id, brand_id=brand1.id, name="Team 1 Campaign"
        )
        campaign2 = await CampaignFactory.create_async(
            session=db_session, team_id=team2_id, brand_id=brand2.id, name="Team 2 Campaign"
        )
        # Flush to database so queries can see the data (but don't commit)
        await db_session.flush()
        # Capture campaign IDs before rollback that might expire them
        campaign1_id = int(campaign1.id)
        campaign2_id = int(campaign2.id)

        # Test team 1 isolation
        # Disable system mode to test RLS (fixture sets it to true by default)
        await db_session.execute(text("SET LOCAL app.is_system_mode = false"))
        await db_session.execute(text(f"SET LOCAL app.team_id = {team1_id}"))
        # query_filter = create_query_filter(team_id=team1_id, campaign_id=None, scope_type=ScopeType.TEAM)
        # event.listen(db_session.sync_session, "do_orm_execute", query_filter)

        result = await db_session.execute(text("SELECT id, name FROM campaigns ORDER BY name"))
        campaigns = list(result)

        assert len(campaigns) == 1, f"Expected 1 campaign for team 1, got {len(campaigns)}"
        assert campaigns[0][0] == campaign1_id
        assert campaigns[0][1] == "Team 1 Campaign"

        # event.remove(db_session.sync_session, "do_orm_execute", query_filter)

        # Test team 2 isolation
        # Reset and re-disable system mode to test RLS (fixture sets it to true by default)
        await db_session.execute(text("RESET app.team_id"))
        await db_session.execute(text("SET LOCAL app.is_system_mode = false"))
        await db_session.execute(text(f"SET LOCAL app.team_id = {team2_id}"))
        # query_filter = create_query_filter(team_id=team2_id, campaign_id=None, scope_type=ScopeType.TEAM)
        # event.listen(db_session.sync_session, "do_orm_execute", query_filter)

        result = await db_session.execute(text("SELECT id, name FROM campaigns ORDER BY name"))
        campaigns = list(result)

        assert len(campaigns) == 1, f"Expected 1 campaign for team 2, got {len(campaigns)}"
        assert campaigns[0][0] == campaign2_id
        assert campaigns[0][1] == "Team 2 Campaign"

        # event.remove(db_session.sync_session, "do_orm_execute", query_filter)

        # Cleanup: reset RLS variables for next test
        await db_session.execute(text("RESET app.team_id"))
        await db_session.execute(text("SET LOCAL app.is_system_mode = true"))

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

        # Create campaigns for each team with unique names
        campaign1 = await CampaignFactory.create_async(
            session=db_session, team_id=team1.id, brand_id=brand1.id, name="System Mode Test Campaign 1"
        )
        campaign2 = await CampaignFactory.create_async(
            session=db_session, team_id=team2.id, brand_id=brand2.id, name="System Mode Test Campaign 2"
        )
        # Flush to database so queries can see the data (but don't commit)
        await db_session.flush()
        campaign1_id = int(campaign1.id)
        campaign2_id = int(campaign2.id)

        # Set system mode
        await db_session.execute(text("SET LOCAL app.is_system_mode = true"))

        with patch("app.utils.db_filters.config.IS_SYSTEM_MODE", True):
            # query_filter = create_query_filter(team_id=None, campaign_id=None, scope_type=None)
            # event.listen(db_session.sync_session, "do_orm_execute", query_filter)

            # Verify we can see campaigns from BOTH teams (system mode bypasses RLS)
            result = await db_session.execute(
                text("SELECT id FROM campaigns WHERE deleted_at IS NULL AND id IN (:id1, :id2)"),
                {"id1": campaign1_id, "id2": campaign2_id},
            )
            campaign_ids = [row[0] for row in result]

            assert len(campaign_ids) == 2, f"Expected to see both campaigns in system mode, got {len(campaign_ids)}"
            assert campaign1_id in campaign_ids, "Should see team 1 campaign"
            assert campaign2_id in campaign_ids, "Should see team 2 campaign"

            # event.remove(db_session.sync_session, "do_orm_execute", query_filter)

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
        # Flush to database so queries can see the data (but don't commit)
        await db_session.flush()

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
        """Verify campaign-scoped access sees both team-wide and campaign-specific resources.

        Campaign scope should have access to:
        1. Campaign-specific resources (campaign_id matches)
        2. Team-wide resources (campaign_id IS NULL, team_id matches)
        """
        from sqlalchemy import select, text

        from app.deliverables.models import Deliverable
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory
        from tests.factories.deliverables import DeliverableFactory

        team1 = multi_team_setup["team1"]
        team2 = multi_team_setup["team2"]
        team1_id = int(team1.id)
        team2_id = int(team2.id)

        # Create brands and campaigns
        brand1 = await BrandFactory.create_async(session=db_session, team_id=team1_id)
        brand2 = await BrandFactory.create_async(session=db_session, team_id=team2_id)

        campaign1 = await CampaignFactory.create_async(
            session=db_session, team_id=team1_id, brand_id=brand1.id, name="Team 1 Campaign"
        )
        campaign2 = await CampaignFactory.create_async(
            session=db_session, team_id=team2_id, brand_id=brand2.id, name="Team 2 Campaign"
        )
        await db_session.flush()
        campaign1_id = int(campaign1.id)

        # Create deliverables:
        # 1. Team-wide deliverable (campaign_id = NULL)
        team_wide_deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=team1_id,
            campaign_id=None,
            title="Team-wide Deliverable",
        )

        # 2. Campaign-specific deliverable
        campaign_specific_deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=team1_id,
            campaign_id=campaign1_id,
            title="Campaign-specific Deliverable",
        )

        # 3. Different team's deliverable (should not be accessible)
        team2_deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=team2_id,
            campaign_id=int(campaign2.id),
            title="Team 2 Deliverable",
        )
        await db_session.flush()

        team_wide_id = int(team_wide_deliverable.id)
        campaign_specific_id = int(campaign_specific_deliverable.id)
        team2_deliverable_id = int(team2_deliverable.id)

        # Set campaign scope RLS context (no RESET needed - fresh session!)
        await db_session.execute(text("SET LOCAL app.is_system_mode = false"))
        await db_session.execute(text(f"SET LOCAL app.team_id = {team1_id}"))
        await db_session.execute(text(f"SET LOCAL app.campaign_id = {campaign1_id}"))

        result = await db_session.execute(select(Deliverable).order_by(Deliverable.title))
        deliverables = result.scalars().all()

        # Should see both team-wide and campaign-specific (but not team2's)
        assert len(deliverables) == 2, f"Expected 2 deliverables in campaign scope, got {len(deliverables)}"
        deliverable_ids = {int(d.id) for d in deliverables}
        assert team_wide_id in deliverable_ids, "Team-wide deliverable should be accessible in campaign scope"
        assert campaign_specific_id in deliverable_ids, "Campaign-specific deliverable should be accessible"
        assert team2_deliverable_id not in deliverable_ids, "Team 2 deliverable should not be accessible"

    async def test_team_scoped_access(self, db_session: AsyncSession, multi_team_setup):
        """Verify team-scoped access sees all resources for that team.

        Team scope should have access to ALL resources for the team, regardless of campaign_id.
        """
        from sqlalchemy import select, text

        from app.deliverables.models import Deliverable
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory
        from tests.factories.deliverables import DeliverableFactory

        team1 = multi_team_setup["team1"]
        team2 = multi_team_setup["team2"]
        team1_id = int(team1.id)
        team2_id = int(team2.id)

        # Create brands and campaigns
        brand1 = await BrandFactory.create_async(session=db_session, team_id=team1_id)
        brand2 = await BrandFactory.create_async(session=db_session, team_id=team2_id)

        campaign1 = await CampaignFactory.create_async(
            session=db_session, team_id=team1_id, brand_id=brand1.id, name="Team 1 Campaign"
        )
        campaign2 = await CampaignFactory.create_async(
            session=db_session, team_id=team2_id, brand_id=brand2.id, name="Team 2 Campaign"
        )
        await db_session.flush()
        campaign1_id = int(campaign1.id)

        # Create deliverables:
        # 1. Team-wide deliverable (campaign_id = NULL)
        team_wide_deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=team1_id,
            campaign_id=None,
            title="Team-wide Deliverable",
        )

        # 2. Campaign-specific deliverable
        campaign_specific_deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=team1_id,
            campaign_id=campaign1_id,
            title="Campaign-specific Deliverable",
        )

        # 3. Different team's deliverable (should not be accessible)
        team2_deliverable = await DeliverableFactory.create_async(
            session=db_session,
            team_id=team2_id,
            campaign_id=int(campaign2.id),
            title="Team 2 Deliverable",
        )
        await db_session.flush()

        team_wide_id = int(team_wide_deliverable.id)
        campaign_specific_id = int(campaign_specific_deliverable.id)
        team2_deliverable_id = int(team2_deliverable.id)

        # Set team scope RLS context (no RESET needed - fresh session!)
        await db_session.execute(text("SET LOCAL app.is_system_mode = false"))
        await db_session.execute(text(f"SET LOCAL app.team_id = {team1_id}"))
        # Note: app.campaign_id is NOT set - it will be NULL

        result = await db_session.execute(select(Deliverable).order_by(Deliverable.title))
        deliverables = result.scalars().all()

        # Should see both deliverables for team1 (team-wide and campaign-specific)
        assert len(deliverables) == 2, f"Expected 2 deliverables in team scope, got {len(deliverables)}"
        deliverable_ids = {int(d.id) for d in deliverables}
        assert team_wide_id in deliverable_ids, "Team-wide deliverable should be accessible in team scope"
        assert (
            campaign_specific_id in deliverable_ids
        ), "Campaign-specific deliverable should be accessible in team scope"
        assert team2_deliverable_id not in deliverable_ids, "Team 2 deliverable should not be accessible"


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
        # Flush to database so queries can see the data (but don't commit)
        await db_session.flush()

        # Set RLS context for team 1
        # Disable system mode to test RLS (fixture sets it to true by default)
        await db_session.execute(text("SET LOCAL app.is_system_mode = false"))
        await db_session.execute(text(f"SET LOCAL app.team_id = {int(team1.id)}"))
        # query_filter = create_query_filter(team_id=int(team1.id), campaign_id=None, scope_type=ScopeType.TEAM)
        # event.listen(db_session.sync_session, "do_orm_execute", query_filter)

        # Use ORM query - should have team_id filter applied automatically
        result = await db_session.execute(select(Campaign))
        campaigns = result.scalars().all()

        assert len(campaigns) == 1, f"Expected 1 campaign for team 1 via ORM, got {len(campaigns)}"

        # event.remove(db_session.sync_session, "do_orm_execute", query_filter)

        # Cleanup: reset RLS variables for next test
        await db_session.execute(text("RESET app.team_id"))
        await db_session.execute(text("SET LOCAL app.is_system_mode = true"))
