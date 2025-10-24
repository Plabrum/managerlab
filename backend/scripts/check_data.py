#!/usr/bin/env python3
"""Check database counts."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.utils.configure import config
from app.campaigns.models import Campaign
from app.users.models import Team, Role
from app.roster.models import Roster
from app.brands.models.brands import Brand


async def check_counts():
    engine = create_async_engine(config.ASYNC_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        teams = await session.execute(select(func.count()).select_from(Team))
        roles = await session.execute(select(func.count()).select_from(Role))
        roster = await session.execute(select(func.count()).select_from(Roster))
        campaigns = await session.execute(select(func.count()).select_from(Campaign))
        brands = await session.execute(select(func.count()).select_from(Brand))

        print(f"Teams: {teams.scalar()}")
        print(f"Roles: {roles.scalar()}")
        print(f"Roster: {roster.scalar()}")
        print(f"Brands: {brands.scalar()}")
        print(f"Campaigns: {campaigns.scalar()}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_counts())
