"""Tests for Row-Level Security (RLS) implementation.

These tests verify that:
1. RLS is enabled on all tables with team_id/campaign_id columns
2. RLS policies exist and are properly configured
3. System mode bypass works as expected
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestRLSConfiguration:
    """Test that RLS is properly configured in the database."""

    async def test_rls_enabled_on_team_scoped_tables(self, db_session: AsyncSession):
        """Verify RLS is enabled on all team-scoped tables."""
        result = await db_session.execute(
            text(
                """
                SELECT tablename, rowsecurity
                FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename IN (
                      'campaigns', 'brands', 'brand_contacts', 'roster',
                      'media', 'documents', 'invoices', 'threads'
                  )
                ORDER BY tablename
            """
            )
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
            text(
                """
                SELECT schemaname, tablename, policyname, permissive, cmd
                FROM pg_policies
                WHERE schemaname = 'public'
                ORDER BY tablename, policyname
            """
            )
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
            text(
                """
                SELECT tablename, policyname, qual
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND policyname = 'team_scope_policy'
                LIMIT 1
            """
            )
        )
        row = result.first()

        assert row is not None, "No team_scope_policy found"

        policy_definition = row[2]
        # Should check for is_system_mode
        assert (
            "app.is_system_mode" in policy_definition or "current_setting('app.is_system_mode'" in policy_definition
        ), "Policy does not check app.is_system_mode for system bypass"

    async def test_system_mode_allows_bypass(self, db_session: AsyncSession):
        """Verify system mode bypasses RLS and allows access to all data."""
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory
        from tests.factories.users import TeamFactory

        # Create two separate teams
        team1 = await TeamFactory.create_async(session=db_session)
        team2 = await TeamFactory.create_async(session=db_session)
        await db_session.flush()

        # Create campaigns with different team IDs
        brand1 = await BrandFactory.create_async(session=db_session, team_id=team1.id)
        brand2 = await BrandFactory.create_async(session=db_session, team_id=team2.id)

        campaign1 = await CampaignFactory.create_async(
            session=db_session,
            team_id=team1.id,
            brand_id=brand1.id,
            name="Team 1 Campaign",
        )
        campaign2 = await CampaignFactory.create_async(
            session=db_session,
            team_id=team2.id,
            brand_id=brand2.id,
            name="Team 2 Campaign",
        )
        await db_session.flush()
        campaign1_id = int(campaign1.id)
        campaign2_id = int(campaign2.id)

        # Ensure system mode is enabled (it should be by default in db_session)
        await db_session.execute(text("SET LOCAL app.is_system_mode = true"))

        # Verify we can see campaigns from BOTH teams (system mode bypasses RLS)
        result = await db_session.execute(
            text("SELECT id FROM campaigns WHERE deleted_at IS NULL AND id IN (:id1, :id2)"),
            {"id1": campaign1_id, "id2": campaign2_id},
        )
        campaign_ids = [row[0] for row in result]

        assert len(campaign_ids) == 2, f"Expected to see both campaigns in system mode, got {len(campaign_ids)}"
        assert campaign1_id in campaign_ids, "Should see team 1 campaign"
        assert campaign2_id in campaign_ids, "Should see team 2 campaign"

    async def test_no_rls_context_blocks_access(self, db_session: AsyncSession):
        """Verify that without RLS context set, no data is accessible."""
        from tests.factories.brands import BrandFactory
        from tests.factories.campaigns import CampaignFactory
        from tests.factories.users import TeamFactory

        # Create team first
        team = await TeamFactory.create_async(session=db_session)
        await db_session.flush()

        # Create brand and campaign using admin session
        brand1 = await BrandFactory.create_async(session=db_session, team_id=team.id)
        await CampaignFactory.create_async(
            session=db_session,
            team_id=team.id,
            brand_id=brand1.id,
            name="Test Campaign",
        )
        await db_session.flush()

        # Disable system mode and don't set any RLS context variables
        await db_session.execute(text("SET LOCAL app.is_system_mode = false"))
        # app.team_id and app.campaign_id are not set

        try:
            # Query campaigns - should see nothing without RLS context
            result = await db_session.execute(text("SELECT COUNT(*) FROM campaigns"))
            count = result.scalar()

            assert count == 0, f"Expected 0 campaigns without RLS context, got {count}"
        finally:
            # Restore system mode for cleanup
            await db_session.execute(text("SET LOCAL app.is_system_mode = true"))
