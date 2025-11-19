"""Script to drop all database tables except alembic_version."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.utils.configure import config


async def nuke_database() -> None:
    """Drop all tables except alembic_version."""
    # Use ADMIN_DB_URL for proper permissions (convert to async)
    admin_url = config.ADMIN_DB_URL.replace("postgresql://", "postgresql+psycopg://")
    engine = create_async_engine(admin_url)
    async with engine.begin() as conn:
        # Drop all RLS policies first
        print("Dropping all RLS policies...")
        result = await conn.execute(
            text("""
                SELECT schemaname, tablename, policyname
                FROM pg_policies
                WHERE schemaname = 'public'
            """)
        )
        policies = result.fetchall()
        for schema, table, policy in policies:
            print(f"  Dropping policy {policy} on {table}")
            await conn.execute(text(f'DROP POLICY IF EXISTS "{policy}" ON "{table}" CASCADE'))

        # Get all tables except alembic_version
        print("\nFetching all tables...")
        result = await conn.execute(
            text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename != 'alembic_version'
            """)
        )
        tables = [row[0] for row in result.fetchall()]

        if not tables:
            print("No tables to drop!")
            return

        print(f"\nFound {len(tables)} tables to drop:")
        for table in tables:
            print(f"  - {table}")

        # Drop all tables
        print("\nDropping tables...")
        for table in tables:
            print(f"  Dropping {table}...")
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

        print("\nDatabase nuked successfully! Only alembic_version remains.")


if __name__ == "__main__":
    asyncio.run(nuke_database())
