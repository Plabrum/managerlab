"""Diagnostic script to check RLS state during test execution."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import *  # noqa: F403


async def diagnose_rls(db_session: AsyncSession):
    """Check RLS configuration and session variables."""

    print("\n" + "=" * 80)
    print("RLS DIAGNOSTIC REPORT")
    print("=" * 80)

    # Check current session variables
    print("\n1. Current Session Variables:")
    result = await db_session.execute(
        text("""
        SELECT
            current_setting('app.is_system_mode', true) as system_mode,
            current_setting('app.team_id', true) as team_id,
            current_setting('app.campaign_id', true) as campaign_id
    """)
    )
    row = result.first()
    assert row is not None, "Failed to get session variables"
    print(f"   app.is_system_mode: {row[0]!r}")
    print(f"   app.team_id: {row[1]!r}")
    print(f"   app.campaign_id: {row[2]!r}")

    # Check NULLIF conversion
    print("\n2. NULLIF Conversion Test:")
    result = await db_session.execute(
        text("""
        SELECT
            NULLIF(current_setting('app.is_system_mode', true), '') as nullif_result,
            NULLIF(current_setting('app.is_system_mode', true), '')::boolean as as_boolean,
            NULLIF(current_setting('app.is_system_mode', true), '')::boolean IS TRUE as final_check
    """)
    )
    row = result.first()
    assert row is not None, "Failed to get NULLIF conversion results"
    print(f"   NULLIF result: {row[0]!r}")
    print(f"   As boolean: {row[1]!r}")
    print(f"   IS TRUE check: {row[2]!r}")

    # Check if RLS is enabled on brands table
    print("\n3. RLS Status on brands table:")
    result = await db_session.execute(
        text("""
        SELECT rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public' AND tablename = 'brands'
    """)
    )
    rls_enabled = result.scalar()
    print(f"   RLS enabled: {rls_enabled}")

    # Check RLS policies
    print("\n4. RLS Policies on brands table:")
    result = await db_session.execute(
        text("""
        SELECT policyname, cmd, qual
        FROM pg_policies
        WHERE schemaname = 'public' AND tablename = 'brands'
    """)
    )
    policies = list(result)
    if policies:
        for policy_name, cmd, qual in policies:
            print(f"   Policy: {policy_name}")
            print(f"   Command: {cmd}")
            print(f"   Condition: {qual[:100]}...")
    else:
        print("   NO POLICIES FOUND!")

    # Test INSERT with current settings
    print("\n5. Test INSERT:")
    try:
        result = await db_session.execute(
            text("""
            INSERT INTO brands (name, team_id, created_at, updated_at)
            VALUES ('Diagnostic Test', 999, NOW(), NOW())
            RETURNING id
        """)
        )
        brand_id = result.scalar()
        print(f"   ✓ INSERT successful! Brand ID: {brand_id}")

        # Clean up
        await db_session.execute(text(f"DELETE FROM brands WHERE id = {brand_id}"))
    except Exception as e:
        print(f"   ✗ INSERT failed: {e}")

    print("\n" + "=" * 80)


async def main():
    """Run diagnostics."""
    # Import fixtures

    from tests.conftest import db_session, setup_database, test_config, test_engine

    # Create fixtures manually
    config = test_config()
    engine = test_engine(config)

    # Setup database
    setup_db = setup_database(engine, config)
    next(setup_db)  # Run setup

    try:
        # Create session
        async for session in db_session(engine, setup_db):
            await diagnose_rls(session)
            break
    finally:
        # Teardown
        try:
            next(setup_db)
        except StopIteration:
            pass


if __name__ == "__main__":
    asyncio.run(main())
