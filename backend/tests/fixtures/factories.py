"""Factory helper fixtures for creating complex test objects."""

from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.brands import BrandContactFactory, BrandFactory
from tests.factories.campaigns import CampaignFactory
from tests.factories.deliverables import DeliverableFactory
from tests.factories.media import MediaFactory
from tests.factories.users import RosterFactory

# ============================================================================
# Factory Helper Fixtures
# ============================================================================


@pytest.fixture
def create_complete_campaign(db_session: AsyncSession):
    """Factory helper to create a campaign with all dependencies.

    Creates: Brand, Roster, Campaign, and optionally Contract.

    Usage:
        async def test_example(create_complete_campaign):
            campaign, brand, roster, contract = await create_complete_campaign(
                add_contract=True
            )
    """

    async def _create(
        add_contract: bool = False,
        campaign_kwargs: dict[str, Any] | None = None,
        brand_kwargs: dict[str, Any] | None = None,
        roster_kwargs: dict[str, Any] | None = None,
        contract_kwargs: dict[str, Any] | None = None,
    ):
        brand = await BrandFactory.create_async(session=db_session, **(brand_kwargs or {}))
        roster = await RosterFactory.create_async(session=db_session, **(roster_kwargs or {}))
        campaign = await CampaignFactory.create_async(session=db_session, brand_id=brand.id, **(campaign_kwargs or {}))

        # Note: ContractFactory doesn't exist yet - contracts feature not implemented
        contract = None
        # if add_contract:
        #     contract = await ContractFactory.create_async(
        #         session=db_session,
        #         campaign_id=campaign.id,
        #         roster_id=roster.id,
        #         **(contract_kwargs or {}),
        #     )

        await db_session.flush()
        return campaign, brand, roster, contract

    return _create


@pytest.fixture
def create_brand_with_contacts(db_session: AsyncSession):
    """Factory helper to create a brand with multiple contacts.

    Usage:
        async def test_example(create_brand_with_contacts):
            brand, contacts = await create_brand_with_contacts(num_contacts=3)
    """

    async def _create(
        num_contacts: int = 2,
        brand_kwargs: dict[str, Any] | None = None,
        contact_kwargs: dict[str, Any] | None = None,
    ):
        brand = await BrandFactory.create_async(session=db_session, **(brand_kwargs or {}))

        contacts = []
        for i in range(num_contacts):
            contact = await BrandContactFactory.create_async(
                session=db_session,
                brand_id=brand.id,
                name=f"Contact {i + 1}",
                email=f"contact{i + 1}@example.com",
                **(contact_kwargs or {}),
            )
            contacts.append(contact)

        await db_session.flush()
        return brand, contacts

    return _create


@pytest.fixture
def create_deliverable_with_media(db_session: AsyncSession):
    """Factory helper to create a deliverable with media associations.

    Usage:
        async def test_example(create_deliverable_with_media):
            deliverable, campaign, media_list = await create_deliverable_with_media(
                num_media=2
            )
    """

    async def _create(
        num_media: int = 1,
        deliverable_kwargs: dict[str, Any] | None = None,
        campaign_kwargs: dict[str, Any] | None = None,
        media_kwargs: dict[str, Any] | None = None,
    ):
        # Create campaign with brand
        brand = await BrandFactory.create_async(session=db_session)
        campaign = await CampaignFactory.create_async(session=db_session, brand_id=brand.id, **(campaign_kwargs or {}))

        # Create deliverable
        deliverable = await DeliverableFactory.create_async(
            session=db_session, campaign_id=campaign.id, **(deliverable_kwargs or {})
        )

        # Create media and associations
        media_list = []
        for i in range(num_media):
            media = await MediaFactory.create_async(session=db_session, **(media_kwargs or {}))
            # Note: DeliverableMediaFactory doesn't exist yet - many-to-many not implemented
            # await DeliverableMediaFactory.create_async(
            #     session=db_session,
            #     deliverable_id=deliverable.id,
            #     media_id=media.id,
            # )
            media_list.append(media)

        await db_session.flush()
        return deliverable, campaign, media_list

    return _create
