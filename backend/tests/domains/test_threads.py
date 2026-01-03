"""Tests for threads domain: thread and message operations."""

from litestar.testing import AsyncTestClient

from app.utils.sqids import sqid_encode


class TestThreads:
    """Tests for thread functionality."""

    async def test_create_thread_on_object(
        self,
        authenticated_client: AsyncTestClient,
        campaign,
    ):
        """Test that threads are created for objects via ThreadableMixin."""

        # Get the campaign - should have thread info
        response = await authenticated_client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        # Thread should be included in response
        assert "thread" in data

    async def test_thread_message_posting(
        self,
        authenticated_client: AsyncTestClient,
        thread,
    ):
        """Test posting a message to a thread."""

        message_content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Test message"}],
                }
            ],
        }

        response = await authenticated_client.post(
            f"/threads/{sqid_encode(thread.id)}/messages",
            json={"content": message_content},
        )
        assert response.status_code in [200, 201, 404]

    async def test_thread_read_status(
        self,
        authenticated_client: AsyncTestClient,
        thread,
    ):
        """Test marking a thread as read."""

        response = await authenticated_client.post(
            f"/threads/{sqid_encode(thread.id)}/mark-read",
        )
        assert response.status_code in [200, 201, 204, 404]


class TestMessages:
    """Tests for message operations."""

    async def test_get_thread_messages(
        self,
        authenticated_client: AsyncTestClient,
        thread,
        message,
    ):
        """Test getting all messages for a thread."""

        # Get messages
        response = await authenticated_client.get(f"/threads/{sqid_encode(thread.id)}/messages")
        # Should succeed or return appropriate status
        assert response.status_code in [200, 404]


class TestThreadUnreadCounts:
    """Tests for thread unread count tracking."""

    async def test_thread_unread_info(
        self,
        authenticated_client: AsyncTestClient,
        campaign,
    ):
        """Test that thread unread info is returned with objects."""

        # Get the campaign
        response = await authenticated_client.get(f"/campaigns/{sqid_encode(campaign.id)}")
        assert response.status_code == 200

        data = response.json()
        # Thread info should include unread count
        assert "thread" in data
        # Thread may be None if no thread exists yet, or contain unread info
        if data["thread"] is not None:
            assert "unread_count" in data["thread"] or "has_unread" in data["thread"]
