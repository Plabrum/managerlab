"""Tests for brands domain: endpoints and basic operations."""

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import assert_rls_isolated, execute_action, get_available_actions
from tests.factories.brands import BrandContactFactory, BrandFactory


class TestBrands:
    """Tests for brand endpoints."""

    async def test_get_brand(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /brands/{id} returns brand details."""
        client, user_data = authenticated_client

        # Create a brand for this team
        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Get the brand
        response = await client.get(f"/brands/{sqid_encode(brand.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(brand.id)
        assert data["name"] == brand.name
        assert data["team_id"] == sqid_encode(user_data["team_id"])
        assert "actions" in data  # Should include available actions

    async def test_update_brand(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test POST /brands/{id} updates brand."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            name="Original Name",
        )
        await db_session.commit()

        # Update the brand
        response = await client.post(
            f"/brands/{sqid_encode(brand.id)}",
            json={"name": "Updated Name"},
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert data["name"] == "Updated Name"

    async def test_list_brand_actions(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /actions/brand_actions/{id} returns available actions."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Get available actions using SQID-encoded ID
        actions = await get_available_actions(client, "brand_actions", sqid_encode(brand.id))

        # Should have at least update and delete actions
        action_keys = [action["action"] for action in actions]
        assert "brand.update" in action_keys
        assert "brand.delete" in action_keys

    async def test_execute_brand_update_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing brand update action."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            name="Before Update",
        )
        await db_session.commit()

        # Execute update action using SQID-encoded ID
        response = await execute_action(
            client,
            "brand_actions",
            "brand.update",
            data={"name": "After Update", "description": "New description"},
            obj_id=sqid_encode(brand.id),
        )

        assert response.status_code in [200, 201, 204]

        # Verify the brand was updated
        await db_session.refresh(brand)
        assert brand.name == "After Update"
        assert brand.description == "New description"

    async def test_execute_brand_delete_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing brand delete action."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()
        brand_id = brand.id

        # Execute delete action using SQID-encoded ID
        response = await execute_action(
            client,
            "brand_actions",
            "brand.delete",
            obj_id=sqid_encode(brand.id),
        )

        assert response.status_code in [200, 201, 204]

        # Verify the brand was soft-deleted
        db_session.expire(brand)
        result = await db_session.execute(select(Brand).where(Brand.id == brand_id))
        deleted_brand = result.scalar_one_or_none()
        # With soft delete, the brand should still exist but be marked as deleted
        assert deleted_brand is not None
        assert deleted_brand.deleted_at is not None

    async def test_brand_rls_isolation(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
        multi_team_setup: dict,
    ):
        """Test that brands are properly isolated by team."""
        client, user_data = authenticated_client

        # Create a brand for team2
        team2_brand = await BrandFactory.create_async(
            session=db_session,
            team_id=multi_team_setup["team2"].id,
        )
        await db_session.commit()

        # Try to access team2's brand with team1's client
        await assert_rls_isolated(client, f"/brands/{sqid_encode(team2_brand.id)}")

    async def test_get_brand_not_found(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /brands/{id} returns 404 for non-existent brand."""
        client, _ = authenticated_client

        # Use a valid SQID for a non-existent ID
        fake_id = sqid_encode(999999999)
        response = await client.get(f"/brands/{fake_id}")
        assert response.status_code == 404


class TestBrandContacts:
    """Tests for brand contact endpoints."""

    async def test_get_brand_contact(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /brands/{brand_id}/contacts/{contact_id} returns contact details."""
        client, user_data = authenticated_client

        # Create a brand and contact
        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        contact = await BrandContactFactory.create_async(
            session=db_session,
            brand_id=brand.id,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Get the contact
        response = await client.get(f"/brands/contacts/{sqid_encode(contact.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(contact.id)
        assert data["first_name"] == contact.first_name
        assert data["last_name"] == contact.last_name

    async def test_update_brand_contact(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test POST /brands/{brand_id}/contacts/{contact_id} updates contact."""
        client, user_data = authenticated_client

        brand = await BrandFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        contact = await BrandContactFactory.create_async(
            session=db_session,
            brand_id=brand.id,
            team_id=user_data["team_id"],
            first_name="Original",
        )
        await db_session.commit()

        # Update the contact
        response = await client.post(
            f"/brands/contacts/{sqid_encode(contact.id)}",
            json={"first_name": "Updated"},
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert data["first_name"] == "Updated"

    async def test_brand_contact_rls_isolation(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
        multi_team_setup: dict,
    ):
        """Test that brand contacts are properly isolated by team."""
        client, user_data = authenticated_client

        # Create a brand and contact for team2
        team2_brand = await BrandFactory.create_async(
            session=db_session,
            team_id=multi_team_setup["team2"].id,
        )
        team2_contact = await BrandContactFactory.create_async(
            session=db_session,
            brand_id=team2_brand.id,
            team_id=multi_team_setup["team2"].id,
        )
        await db_session.commit()

        # Try to access team2's contact with team1's client
        await assert_rls_isolated(client, f"/brands/contacts/{sqid_encode(team2_contact.id)}")
