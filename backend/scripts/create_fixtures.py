#!/usr/bin/env python3
"""Script to populate the database with fake data for development."""

import asyncio
import random
import sys
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.utils.configure import config

# Import all models to ensure SQLAlchemy relationships are registered
from tests.factories import (
    BrandContactFactory,
    BrandFactory,
    CampaignFactory,
    DeliverableFactory,
    GoogleOAuthAccountFactory,
    InvoiceFactory,
    MediaFactory,
    RoleFactory,
    RosterFactory,
    TeamFactory,
    UserFactory,
)


async def create_fixtures():
    """Create fake data for development."""
    print("🚀 Creating database fixtures...")

    # Create async engine and session
    engine = create_async_engine(config.ASYNC_DATABASE_URL, echo=False)
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session_factory() as session:
        try:
            # Create teams first
            print("📝 Creating teams...")
            teams = []
            for i in range(3):
                team = TeamFactory.build()
                session.add(team)
                teams.append(team)
            await session.flush()

            # Create users with Google OAuth accounts
            print("👥 Creating users with Google OAuth accounts...")
            users = []
            for i in range(10):
                user = UserFactory.build()
                session.add(user)
                await session.flush()

                # Create Google OAuth account for each user
                oauth_account = GoogleOAuthAccountFactory.build(user_id=user.id)
                session.add(oauth_account)
                users.append(user)

            await session.flush()

            # Create roles to assign users to teams
            print("🔑 Creating roles (assigning users to teams)...")
            roles = []
            for user in users:
                # Assign each user to a random team
                team = random.choice(teams)
                role = RoleFactory.build(user_id=user.id, team_id=team.id)
                session.add(role)
                roles.append(role)
            await session.flush()

            # Create roster members (talent) owned by users
            print("⭐ Creating roster members...")
            roster = []
            for i in range(25):
                # Assign roster member to a random user
                user = random.choice(users)
                roster_member = RosterFactory.build(user_id=user.id)
                session.add(roster_member)
                roster.append(roster_member)
            await session.flush()

            # Create brands
            print("🏢 Creating brands...")
            brands = []
            for i in range(8):
                brand = BrandFactory.build()
                session.add(brand)
                brands.append(brand)
            await session.flush()

            # Create brand contacts (multiple per brand)
            print("📞 Creating brand contacts...")
            brand_contacts = []
            for brand in brands:
                for j in range(3):
                    contact = BrandContactFactory.build(brand_id=brand.id)
                    session.add(contact)
                    brand_contacts.append(contact)

            await session.flush()

            # Create campaigns
            print("🎯 Creating campaigns...")
            campaigns = []
            for brand in brands:
                # Each brand gets 2-4 campaigns
                for j in range(3):
                    campaign = CampaignFactory.build(brand_id=brand.id)
                    session.add(campaign)
                    campaigns.append(campaign)

            await session.flush()

            # Create media assets
            print("🖼️ Creating media assets...")
            media_assets = []
            for i in range(20):
                media = MediaFactory.build()
                session.add(media)
                media_assets.append(media)
            await session.flush()

            # Create deliverables for campaigns
            print("📱 Creating deliverables...")
            deliverables = []
            for campaign in campaigns:
                # Each campaign gets 2-5 deliverables
                for j in range(4):
                    deliverable = DeliverableFactory.build(campaign_id=campaign.id)
                    session.add(deliverable)
                    deliverables.append(deliverable)

            await session.flush()

            # Associate deliverables with media (many-to-many relationship)
            print("🔗 Associating deliverables with media...")
            from app.deliverables.models import DeliverableMedia

            for deliverable in deliverables:
                # Each deliverable gets 1-3 media assets
                selected_media = random.sample(media_assets, min(3, len(media_assets)))
                for media in selected_media:
                    assoc = DeliverableMedia(deliverable_id=deliverable.id, media_id=media.id)
                    session.add(assoc)

            await session.flush()

            # Associate campaigns with lead contacts (many-to-many relationship) using direct SQL
            print("🤝 Associating campaigns with lead contacts...")
            from app.campaigns.models import campaign_lead_contacts

            for campaign in campaigns:
                # Get contacts from the same brand
                brand_contacts_for_campaign = [
                    contact for contact in brand_contacts if contact.brand_id == campaign.brand_id
                ]
                if brand_contacts_for_campaign:
                    # Each campaign gets 1-2 lead contacts
                    selected_contacts = random.sample(
                        brand_contacts_for_campaign,
                        min(2, len(brand_contacts_for_campaign)),
                    )
                    for contact in selected_contacts:
                        insert_stmt = campaign_lead_contacts.insert().values(
                            campaign_id=campaign.id, brand_contact_id=contact.id
                        )
                        await session.execute(insert_stmt)

            await session.flush()

            # Create invoices for campaigns
            print("💰 Creating invoices...")
            for campaign in campaigns:
                # Each campaign gets 1-2 invoices
                for k in range(2):
                    invoice = InvoiceFactory.build(campaign_id=campaign.id)
                    session.add(invoice)

            await session.flush()

            # Commit all changes
            await session.commit()

            print("✅ Fixtures created successfully!")
            print("   📊 Summary:")
            print(f"   - {len(teams)} teams")
            print(f"   - {len(users)} users with OAuth accounts")
            print(f"   - {len(roles)} roles (user-team assignments)")
            print(f"   - {len(roster)} roster members (talent)")
            print(f"   - {len(brands)} brands")
            print(f"   - {len(brand_contacts)} brand contacts")
            print(f"   - {len(campaigns)} campaigns")
            print(f"   - {len(deliverables)} deliverables")
            print(f"   - {len(media_assets)} media assets")
            print(f"   - {len(campaigns) * 2} invoices")

        except Exception as e:
            print(f"❌ Error creating fixtures: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_fixtures())
