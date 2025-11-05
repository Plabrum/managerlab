"""Tests for documents domain: endpoints and basic operations."""

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.enums import DocumentStates
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import execute_action, get_available_actions
from tests.factories.documents import DocumentFactory  # Still needed for some specific tests


class TestDocuments:
    """Tests for document endpoints."""

    async def test_get_document(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        document,
    ):
        """Test GET /documents/{id} returns document details."""
        client, user_data = authenticated_client

        # Get the document
        response = await client.get(f"/documents/{sqid_encode(document.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(document.id)
        assert data["file_name"] == document.file_name
        assert data["file_type"] == document.file_type
        assert data["state"] == document.state.value
        assert "actions" in data  # Should include available actions

    async def test_presigned_upload_request(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test POST /documents/presigned-upload returns presigned URL."""
        client, user_data = authenticated_client

        # Request presigned upload URL
        response = await client.post(
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
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test POST /documents/register creates document record."""
        client, _ = authenticated_client

        response = await client.post(
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
        authenticated_client: tuple[AsyncTestClient, dict],
        document,
    ):
        """Test GET /actions/document_actions/{id} returns available actions."""
        client, user_data = authenticated_client

        # Get available actions
        actions = await get_available_actions(client, "document_actions", sqid_encode(document.id))

        # Should have at least delete action
        action_keys = [action["action"] for action in actions]
        assert "document_actions__document_delete" in action_keys

    async def test_execute_document_delete_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        document,
        db_session: AsyncSession,
    ):
        """Test executing document delete action."""
        client, _ = authenticated_client

        result = await execute_action(
            client,
            "document_actions",
            "document_actions__document_delete",
            {},
            sqid_encode(document.id),
        )

        assert result is not None

    async def test_get_document_not_found(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /documents/{id} with non-existent ID returns 404."""
        client, user_data = authenticated_client

        # Try to get a non-existent document
        response = await client.get(f"/documents/{sqid_encode(99999)}")
        assert response.status_code == 404

    # Removed test_document_with_campaign_scope - RLS/scope testing should be in integration tests


class TestDocumentFileValidation:
    """Tests for document file validation."""

    async def test_file_size_validation(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test that file size limit is enforced."""
        client, user_data = authenticated_client

        # Try to upload a file that's too large (>100MB)
        response = await client.post(
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
