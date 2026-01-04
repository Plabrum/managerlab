"""Common object fixtures for convenient testing."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.brands import BrandFactory
from tests.factories.campaigns import CampaignFactory
from tests.factories.deliverables import DeliverableFactory
from tests.factories.documents import DocumentFactory
from tests.factories.payments import InvoiceFactory
from tests.factories.threads import MessageFactory, ThreadFactory
from tests.factories.users import RosterFactory

# ============================================================================
# Common Object Fixtures for Tests
# ============================================================================


@pytest.fixture
async def team(db_session: AsyncSession):
    """Create a team for testing.

    Returns:
        Team instance
    """
    from tests.factories.users import TeamFactory

    team = await TeamFactory.create_async(session=db_session)
    await db_session.flush()
    return team


@pytest.fixture
async def user(db_session: AsyncSession, team):
    """Create a user linked to the team.

    Returns:
        User instance
    """
    from app.users.models import Role
    from tests.factories.users import UserFactory

    user = await UserFactory.create_async(session=db_session)

    # Link user to team with member role
    role = Role(user_id=user.id, team_id=team.id, role_level="member")
    db_session.add(role)

    await db_session.flush()
    return user


@pytest.fixture
async def brand(
    team,
    db_session: AsyncSession,
):
    """Create a brand associated with the given team.

    Returns:
        Brand instance
    """
    brand = await BrandFactory.create_async(
        session=db_session,
        team_id=team.id,
    )
    await db_session.flush()
    return brand


@pytest.fixture
async def campaign(
    team,
    brand,
    db_session: AsyncSession,
):
    """Create a campaign with a brand, associated with the given team.

    Returns:
        Campaign instance
    """
    campaign = await CampaignFactory.create_async(
        session=db_session,
        team_id=team.id,
        brand_id=brand.id,
    )
    await db_session.flush()
    return campaign


@pytest.fixture
async def roster(
    team,
    user,
    db_session: AsyncSession,
):
    """Create a roster member associated with the given team.

    Returns:
        Roster instance
    """
    roster = await RosterFactory.create_async(
        session=db_session,
        team_id=team.id,
        user_id=user.id,
        profile_photo_id=None,  # Don't create a profile photo by default
    )
    await db_session.flush()
    return roster


@pytest.fixture
async def deliverable(
    team,
    campaign,
    db_session: AsyncSession,
):
    """Create a deliverable associated with the given campaign.

    Returns:
        Deliverable instance
    """
    deliverable = await DeliverableFactory.create_async(
        session=db_session,
        team_id=team.id,
        campaign_id=campaign.id,
    )
    await db_session.flush()
    return deliverable


@pytest.fixture
async def document(
    team,
    db_session: AsyncSession,
):
    """Create a document associated with the given team.

    Returns:
        Document instance
    """
    document = await DocumentFactory.create_async(
        session=db_session,
        team_id=team.id,
    )
    await db_session.flush()
    return document


@pytest.fixture
async def invoice(
    team,
    db_session: AsyncSession,
):
    """Create an invoice associated with the given team.

    Returns:
        Invoice instance
    """
    invoice = await InvoiceFactory.create_async(
        session=db_session,
        team_id=team.id,
    )
    await db_session.flush()
    return invoice


@pytest.fixture
async def thread(
    team,
    campaign,
    db_session: AsyncSession,
):
    """Create a thread associated with a campaign.

    Returns:
        Thread instance
    """
    thread = await ThreadFactory.create_async(
        session=db_session,
        team_id=team.id,
        threadable_type="Campaign",
        threadable_id=campaign.id,
    )
    await db_session.flush()
    return thread


@pytest.fixture
async def message(
    team,
    user,
    thread,
    campaign,
    db_session: AsyncSession,
):
    """Create a message in a thread.

    Returns:
        Message instance
    """
    # Set campaign_id if the thread is for a campaign
    campaign_id = campaign.id if thread.threadable_type == "Campaign" else None

    message = await MessageFactory.create_async(
        session=db_session,
        team_id=team.id,
        thread_id=thread.id,
        user_id=user.id,
        campaign_id=campaign_id,
    )
    await db_session.flush()
    return message
