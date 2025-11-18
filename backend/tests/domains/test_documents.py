"""Tests for documents domain: endpoints and basic operations."""

from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import execute_action, get_available_actions


class TestDocuments:
    """Tests for document endpoints."""

    async def test_get_document(
        self,
        authenticated_client: AsyncTestClient,
        document,
    ):
        """Test GET /documents/{id} returns document details."""

        # Get the document
        response = await authenticated_client.get(f"/documents/{sqid_encode(document.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(document.id)
        assert data["file_name"] == document.file_name
        assert data["file_type"] == document.file_type
        assert data["state"] == document.state.value
        assert "actions" in data  # Should include available actions

    async def test_presigned_upload_request(
        self,
        authenticated_client: AsyncTestClient,
    ):
        """Test POST /documents/presigned-upload returns presigned URL."""

        # Request presigned upload URL
        response = await authenticated_client.post(
            "/documents/presigned-upload",
            json={
                "file_name": "test.pdf",
                "file_size": 1024 * 100,  # 100KB
                "content_type": "application/pdf",
            },
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert "upload_url" in data
        assert "file_key" in data
        assert data["file_key"].startswith("documents/")
        assert "test.pdf" in data["file_key"]

    async def test_register_document(
        self,
        authenticated_client: AsyncTestClient,
        db_session: AsyncSession,
    ):
        """Test POST /documents/register creates document record."""

        response = await authenticated_client.post(
            "/documents/register",
            json={
                "file_key": "documents/test-key/test.pdf",
                "file_name": "test.pdf",
                "file_size": 1024 * 100,
                "mime_type": "application/pdf",
            },
        )
        assert response.status_code in [200, 201]
        assert response.json() is not None

    async def test_list_document_actions(
        self,
        authenticated_client: AsyncTestClient,
        document,
    ):
        """Test GET /actions/document_actions/{id} returns available actions."""

        # Get available actions
        actions = await get_available_actions(authenticated_client, "document_actions", sqid_encode(document.id))

        # Should have at least delete action
        action_keys = [action["action"] for action in actions]
        assert "document_actions__document_delete" in action_keys

    async def test_execute_document_delete_action(
        self,
        authenticated_client: AsyncTestClient,
        document,
        db_session: AsyncSession,
    ):
        """Test executing document delete action."""

        result = await execute_action(
            authenticated_client,
            "document_actions",
            "document_actions__document_delete",
            {},
            sqid_encode(document.id),
        )

        assert result is not None

    async def test_get_document_not_found(
        self,
        authenticated_client: AsyncTestClient,
    ):
        """Test GET /documents/{id} with non-existent ID returns 404."""

        # Try to get a non-existent document
        response = await authenticated_client.get(f"/documents/{sqid_encode(99999)}")
        assert response.status_code == 404

    # Removed test_document_with_campaign_scope - RLS/scope testing should be in integration tests


class TestDocumentFileValidation:
    """Tests for document file validation."""

    async def test_file_size_validation(
        self,
        authenticated_client: AsyncTestClient,
    ):
        """Test that file size limit is enforced."""

        # Try to upload a file that's too large (>100MB)
        response = await authenticated_client.post(
            "/documents/presigned-upload",
            json={
                "file_name": "huge.pdf",
                "file_size": 1024 * 1024 * 150,  # 150MB
                "content_type": "application/pdf",
            },
        )
        # Should fail validation
        assert response.status_code == 400
        assert "exceeds maximum" in response.text.lower()
