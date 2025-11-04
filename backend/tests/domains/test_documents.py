"""Tests for documents domain: endpoints and basic operations."""

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.enums import DocumentStates
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import assert_rls_isolated, execute_action, get_available_actions
from tests.factories.documents import DocumentFactory


class TestDocuments:
    """Tests for document endpoints."""

    async def test_get_document(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /documents/{id} returns document details."""
        client, user_data = authenticated_client

        # Create a document for this team
        document = await DocumentFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

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
        client, user_data = authenticated_client

        # Register a document
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

        data = response.json()
        assert data["file_name"] == "test.pdf"
        assert data["file_type"] == "pdf"
        assert data["state"] == DocumentStates.READY.value
        assert data["team_id"] == sqid_encode(user_data["team_id"])

    async def test_list_document_actions(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /actions/document_actions/{id} returns available actions."""
        client, user_data = authenticated_client

        document = await DocumentFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Get available actions
        actions = await get_available_actions(client, "document_actions", sqid_encode(document.id))

        # Should have at least delete action
        action_keys = [action["action"] for action in actions]
        assert "document.delete" in action_keys

    async def test_execute_document_delete_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing document delete action."""
        client, user_data = authenticated_client

        document = await DocumentFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Execute delete action
        result = await execute_action(
            client,
            "document_actions",
            "document.delete",
            {},
            sqid_encode(document.id),
        )

        # Verify deletion (soft delete)
        assert result["success"] is True

        # Verify document is soft-deleted
        await db_session.refresh(document)
        assert document.deleted_at is not None

    async def test_document_rls_isolation(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        other_team_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that teams cannot access each other's documents."""
        client, user_data = authenticated_client
        other_client, other_user_data = other_team_client

        # Create document for first team
        document = await DocumentFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Verify RLS isolation
        await assert_rls_isolated(
            client=other_client,
            resource_path=f"/documents/{sqid_encode(document.id)}",
        )

    async def test_get_document_not_found(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /documents/{id} with non-existent ID returns 404."""
        client, user_data = authenticated_client

        # Try to get a non-existent document
        response = await client.get(f"/documents/{sqid_encode(99999)}")
        assert response.status_code == 404

    async def test_document_with_campaign_scope(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test creating document with campaign_id in scope."""
        from tests.factories.campaigns import CampaignFactory

        client, user_data = authenticated_client

        # Create a campaign
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Set campaign scope by updating session data
        await client.set_session_data(
            {
                "user_id": user_data["user_id"],
                "team_id": user_data["team_id"],
                "scope_type": "CAMPAIGN",
                "campaign_id": campaign.id,
            }
        )

        # Register document with campaign scope
        response = await client.post(
            "/documents/register",
            json={
                "file_key": "documents/test-campaign/doc.pdf",
                "file_name": "campaign-doc.pdf",
                "file_size": 1024 * 50,
                "mime_type": "application/pdf",
            },
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert data["campaign_id"] == sqid_encode(campaign.id)


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
