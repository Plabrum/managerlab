#!/usr/bin/env python3
"""Script to populate the database with realistic invoice data for development."""

import asyncio
import random
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Import other models to ensure relationships are configured
from app.auth.google.models import GoogleOAuthAccount  # noqa: F401
from app.auth.models import MagicLinkToken  # noqa: F401
from app.brands.models.brands import Brand  # noqa: F401
from app.brands.models.contacts import BrandContact  # noqa: F401

# Import all models to ensure SQLAlchemy relationships are registered
from app.campaigns.models import Campaign  # noqa: F401
from app.deliverables.models import Deliverable  # noqa: F401
from app.documents.models import Document  # noqa: F401
from app.media.models import Media  # noqa: F401
from app.payments.enums import InvoiceStates
from app.payments.models import Invoice
from app.roster.models import Roster  # noqa: F401
from app.teams.models import Team  # noqa: F401
from app.users.models import User  # noqa: F401
from app.utils.configure import config


async def create_realistic_invoices():
    """Create realistic invoice data with varied states and payment status."""
    print("💰 Creating realistic invoice data...")

    # Use postgres superuser connection to bypass RLS
    # Replace user:password in the connection string with 'postgres:postgres'
    import re

    postgres_url = re.sub(r"//[^:]+:[^@]+@", "//postgres:postgres@", config.ASYNC_DATABASE_URL)

    print("💡 Using postgres superuser to bypass RLS policies")

    # Create async engine and session
    engine = create_async_engine(postgres_url, echo=False)
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session_factory() as session:
        try:
            # No need to manually bypass RLS - postgres user bypasses it automatically

            # Get all campaigns
            result = await session.execute(sa.select(Campaign))
            campaigns = list(result.scalars().all())

            if not campaigns:
                print("❌ No campaigns found. Please run create_fixtures.py first.")
                return

            print(f"📊 Found {len(campaigns)} campaigns")

            # Invoice scenarios to create
            scenarios = [
                {
                    "name": "Draft Invoice (not yet sent)",
                    "state": InvoiceStates.DRAFT,
                    "paid_percentage": 0.0,
                    "days_ago_posted": None,
                    "due_in_days": 30,
                },
                {
                    "name": "Posted Invoice (recently sent, unpaid)",
                    "state": InvoiceStates.POSTED,
                    "paid_percentage": 0.0,
                    "days_ago_posted": random.randint(1, 7),
                    "due_in_days": random.randint(15, 30),
                },
                {
                    "name": "Posted Invoice (partially paid)",
                    "state": InvoiceStates.POSTED,
                    "paid_percentage": random.uniform(0.25, 0.75),
                    "days_ago_posted": random.randint(10, 30),
                    "due_in_days": random.randint(5, 20),
                },
                {
                    "name": "Posted Invoice (fully paid)",
                    "state": InvoiceStates.POSTED,
                    "paid_percentage": 1.0,
                    "days_ago_posted": random.randint(30, 90),
                    "due_in_days": random.randint(-10, 10),  # Some past due, some future
                },
                {
                    "name": "Posted Invoice (overdue, unpaid)",
                    "state": InvoiceStates.POSTED,
                    "paid_percentage": 0.0,
                    "days_ago_posted": random.randint(45, 90),
                    "due_in_days": random.randint(-30, -1),  # Negative = overdue
                },
                {
                    "name": "Posted Invoice (overdue, partially paid)",
                    "state": InvoiceStates.POSTED,
                    "paid_percentage": random.uniform(0.1, 0.6),
                    "days_ago_posted": random.randint(60, 120),
                    "due_in_days": random.randint(-60, -15),
                },
            ]

            # Company names and services for variety
            company_names = [
                "Acme Corporation",
                "TechStart Inc.",
                "Global Solutions Ltd",
                "Innovation Partners",
                "Digital Ventures",
                "Creative Studios",
                "Modern Brands Co",
                "Enterprise Systems",
                "Cloud Dynamics",
                "Next Gen Media",
                "Velocity Partners",
                "Horizon Technologies",
                "Pinnacle Group",
                "Strategic Innovations",
                "Synergy Solutions",
            ]

            service_descriptions = [
                "Social media content creation and management services",
                "Influencer marketing campaign for Q4 product launch",
                "Brand partnership and sponsored content production",
                "Multi-platform content creation and distribution",
                "Video production and post-production services",
                "Photography and creative direction for brand campaign",
                "Content strategy and execution for social channels",
                "Sponsored posts and story content across platforms",
                "Product review and unboxing content series",
                "Brand ambassador services and content creation",
                "Live streaming event coverage and promotion",
                "Tutorial and educational content production",
                "Behind-the-scenes content and brand storytelling",
                "Seasonal campaign content and creative assets",
                "Product launch promotion and awareness campaign",
            ]

            # Invoice amount ranges (in USD)
            amount_ranges = [
                (500, 2000),  # Small campaigns
                (2000, 5000),  # Medium campaigns
                (5000, 15000),  # Large campaigns
                (15000, 50000),  # Major campaigns
            ]

            invoices_created = 0
            invoice_number_start = 10000 + random.randint(0, 5000)

            # Create 2-4 invoices per campaign with varied scenarios
            for campaign in campaigns:
                num_invoices = random.randint(2, 4)

                for i in range(num_invoices):
                    # Pick a random scenario
                    scenario = random.choice(scenarios)

                    # Generate random amount
                    amount_range = random.choice(amount_ranges)
                    amount_due = Decimal(str(random.uniform(amount_range[0], amount_range[1]))).quantize(
                        Decimal("0.01")
                    )

                    # Calculate amount paid
                    amount_paid = (amount_due * Decimal(str(scenario["paid_percentage"]))).quantize(Decimal("0.01"))

                    # Calculate dates
                    if scenario["days_ago_posted"] is not None:
                        posting_date = (datetime.now(tz=UTC) - timedelta(days=scenario["days_ago_posted"])).date()
                    else:
                        posting_date = datetime.now(tz=UTC).date()

                    due_date = (datetime.now(tz=UTC) + timedelta(days=scenario["due_in_days"])).date()

                    # Create invoice
                    invoice = Invoice(
                        invoice_number=invoice_number_start + invoices_created,
                        customer_name=random.choice(company_names),
                        customer_email=f"{random.choice(company_names).lower().replace(' ', '')}@example.com",
                        posting_date=posting_date,
                        due_date=due_date,
                        amount_due=amount_due,
                        amount_paid=amount_paid,
                        description=random.choice(service_descriptions),
                        notes=None
                        if random.random() > 0.3
                        else random.choice(
                            [
                                "Payment terms: NET-30",
                                "50% deposit paid upfront",
                                "Final payment upon content delivery",
                                "Payment plan: 3 installments",
                                "Milestone-based payment structure",
                                "Includes usage rights and exclusivity",
                            ]
                        ),
                        state=scenario["state"],
                        campaign_id=campaign.id,
                    )

                    session.add(invoice)
                    invoices_created += 1

            await session.flush()
            await session.commit()

            print(f"✅ Created {invoices_created} realistic invoices!")
            print("\n📊 Invoice Summary:")

            # Count by state
            result = await session.execute(sa.select(Invoice).where(Invoice.state == InvoiceStates.DRAFT))
            draft_count = len(list(result.scalars().all()))

            result = await session.execute(sa.select(Invoice).where(Invoice.state == InvoiceStates.POSTED))
            posted_count = len(list(result.scalars().all()))

            result = await session.execute(
                sa.select(Invoice).where(
                    Invoice.state == InvoiceStates.POSTED,
                    Invoice.amount_paid >= Invoice.amount_due,
                )
            )
            fully_paid_count = len(list(result.scalars().all()))

            result = await session.execute(
                sa.select(Invoice).where(
                    Invoice.state == InvoiceStates.POSTED,
                    Invoice.amount_paid > 0,
                    Invoice.amount_paid < Invoice.amount_due,
                )
            )
            partially_paid_count = len(list(result.scalars().all()))

            result = await session.execute(
                sa.select(Invoice).where(
                    Invoice.state == InvoiceStates.POSTED,
                    Invoice.due_date < datetime.now(tz=UTC).date(),
                    Invoice.amount_paid < Invoice.amount_due,
                )
            )
            overdue_count = len(list(result.scalars().all()))

            print(f"   - {draft_count} draft invoices")
            print(f"   - {posted_count} posted invoices")
            print(f"   - {fully_paid_count} fully paid")
            print(f"   - {partially_paid_count} partially paid")
            print(f"   - {overdue_count} overdue")

        except Exception as e:
            print(f"❌ Error creating invoices: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_realistic_invoices())
