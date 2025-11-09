"""Tests for brands domain: endpoints and basic operations."""

from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.enums import ActionGroupType
from app.utils.sqids import sqid_encode
from tests.factories.brands import BrandContactFactory


class TestBrands:
    """Tests for brand endpoints."""

    async def test_get_brand(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        brand,
    ):
        """Test GET /brands/{id} returns brand details."""
        client, _ = authenticated_client

        response = await client.get(f"/brands/{sqid_encode(brand.id)}")
        assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
        assert response.json() is not None

    async def test_update_brand(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        brand,
    ):
        """Test POST /brands/{id} updates brand."""
        client, _ = authenticated_client

        response = await client.post(
            f"/brands/{sqid_encode(brand.id)}",
            json={"name": "Updated Name"},
        )
        assert response.status_code in [200, 201]
        assert response.json() is not None

    async def test_list_top_level_brand_actions(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /actions/brand_actions returns only top-level actions (no object)."""
        client, _ = authenticated_client

        response = await client.get("/actions/brand_actions")
        assert response.status_code == 200
        data = response.json()
        assert data is not None

        # Should only contain CreateBrand action (top-level)
        actions = data.get("actions", [])
        action_keys = [action["action"] for action in actions]

        # Verify CreateBrand is present
        assert "brand_actions__brand_create" in action_keys

        # Verify object actions (DeleteBrand, UpdateBrand) are NOT present
        assert "brand_actions__brand_delete" not in action_keys
        assert "brand_actions__brand_update" not in action_keys

    async def test_list_brand_object_actions(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        brand,
    ):
        """Test GET /actions/brand_actions/{id} returns only object actions."""
        client, _ = authenticated_client

        response = await client.get(f"/actions/brand_actions/{sqid_encode(brand.id)}")
        assert response.status_code == 200
        data = response.json()
        assert data is not None

        # Should only contain object actions (DeleteBrand, UpdateBrand)
        actions = data.get("actions", [])
        action_keys = [action["action"] for action in actions]

        # Verify object actions are present
        assert "brand_actions__brand_delete" in action_keys
        assert "brand_actions__brand_update" in action_keys

        # Verify CreateBrand (top-level) is NOT present
        assert "brand_actions__brand_create" not in action_keys

    async def test_execute_brand_update_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        brand,
    ):
        """Test executing brand update action."""
        client, _ = authenticated_client

        response = await client.post(
            f"/actions/{ActionGroupType.BrandActions}/{sqid_encode(brand.id)}",
            json={
                "action": "brand_actions__brand_update",
                "data": {"name": "After Update"},
            },
        )
        assert response.status_code in [
            200,
            201,
            204,
        ], f"Got {response.status_code}: {response.text}"
        assert response.json() is not None

    async def test_execute_brand_delete_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        brand,
    ):
        """Test executing brand delete action."""
        client, _ = authenticated_client

        response = await client.post(
            f"/actions/brand_actions/{sqid_encode(brand.id)}",
            json={"action": "brand_actions__brand_delete"},
        )
        assert response.status_code in [200, 201, 204]
        assert response.json() is not None

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
        brand,
        db_session: AsyncSession,
    ):
        """Test GET /brands/contacts/{contact_id} returns contact details."""
        client, user_data = authenticated_client

        contact = await BrandContactFactory.create_async(
            session=db_session,
            brand_id=brand.id,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        response = await client.get(f"/brands/contacts/{sqid_encode(contact.id)}")
        assert response.status_code == 200
        assert response.json() is not None

    async def test_update_brand_contact(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        brand,
        db_session: AsyncSession,
    ):
        """Test POST /brands/contacts/{contact_id} updates contact."""
        client, user_data = authenticated_client

        contact = await BrandContactFactory.create_async(
            session=db_session,
            brand_id=brand.id,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        response = await client.post(
            f"/brands/contacts/{sqid_encode(contact.id)}",
            json={"first_name": "Updated"},
        )
        assert response.status_code in [200, 201]
        assert response.json() is not None
