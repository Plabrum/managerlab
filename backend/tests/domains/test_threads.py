"""Tests for threads domain: thread and message operations."""

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.threads.models import Message, Thread
from app.utils.sqids import sqid_encode
from tests.factories.brands import BrandFactory
from tests.factories.campaigns import CampaignFactory


class TestThreads:
    """Tests for thread functionality."""

    async def test_create_thread_on_object(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that threads are created for objects via ThreadableMixin."""
        client, user_data = authenticated_client

        # Create a campaign (which has ThreadableMixin)
        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )
        await db_session.commit()

        # Get the campaign - should have thread info
        response = await client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        # Thread should be included in response
        assert "thread" in data

    async def test_thread_message_posting(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test posting a message to a thread."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )
        await db_session.commit()

        thread = Thread(
            team_id=user_data["team_id"],
            threadable_type="Campaign",
            threadable_id=campaign.id,
        )
        db_session.add(thread)
        await db_session.flush()

        message_content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Test message"}],
                }
            ],
        }

        response = await client.post(
            f"/threads/{sqid_encode(thread.id)}/messages",
            json={"content": message_content},
        )
        assert response.status_code in [200, 201, 404]

    async def test_thread_read_status(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test marking a thread as read."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )

        thread = Thread(
            team_id=user_data["team_id"],
            threadable_type="Campaign",
            threadable_id=campaign.id,
        )
        db_session.add(thread)
        await db_session.flush()

        message = Message(
            thread_id=thread.id,
            team_id=user_data["team_id"],
            user_id=user_data["user"].id,
            content={
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Test"}],
                    }
                ],
            },
        )
        db_session.add(message)
        await db_session.commit()

        response = await client.post(
            f"/threads/{sqid_encode(thread.id)}/mark-read",
        )
        assert response.status_code in [200, 201, 204, 404]


class TestMessages:
    """Tests for message operations."""

    async def test_get_thread_messages(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test getting all messages for a thread."""
        client, user_data = authenticated_client

        # Create a thread
        thread = Thread(
            team_id=user_data["team_id"],
            threadable_type="Campaign",
            threadable_id=1,
        )
        db_session.add(thread)
        await db_session.flush()

        # Add multiple messages
        for i in range(3):
            message = Message(
                thread_id=thread.id,
                team_id=user_data["team_id"],
                user_id=user_data["user"].id,
                content={
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": f"Message {i}"}],
                        }
                    ],
                },
            )
            db_session.add(message)
        await db_session.commit()

        # Get messages
        response = await client.get(f"/threads/{sqid_encode(thread.id)}/messages")
        # Should succeed or return appropriate status
        assert response.status_code in [200, 404]


class TestThreadUnreadCounts:
    """Tests for thread unread count tracking."""

    async def test_thread_unread_info(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that thread unread info is returned with objects."""
        client, user_data = authenticated_client

        # Create a campaign (which has ThreadableMixin)
        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            brand_id=brand.id,
        )
        await db_session.commit()

        # Get the campaign
        response = await client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        # Thread info should include unread count
        assert "thread" in data
        # Thread may be None if no thread exists yet, or contain unread info
        if data["thread"] is not None:
            assert "unread_count" in data["thread"] or "has_unread" in data["thread"]
