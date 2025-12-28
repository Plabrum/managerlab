"""Tests for views domain: endpoints and basic operations."""

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.enums import ObjectTypes
from app.utils.sqids import sqid_encode
from app.views.models import SavedView


class TestViews:
    """Tests for view CRUD endpoints."""

    async def test_create_personal_view(
        self,
        authenticated_client: AsyncTestClient,
        team,
        user,
        db_session: AsyncSession,
    ):
        """Test POST /views/{object_type} creates a personal view."""
        view_data = {
            "name": "My Roster View",
            "object_type": "roster",  # Must match path parameter
            "is_personal": True,
            "config": {
                "display_mode": "table",
                "column_filters": [],
                "column_visibility": {},
                "sorting": [],
                "page_size": 40,
            },
        }

        response = await authenticated_client.post("/views/roster", json=view_data)
        assert response.status_code == 201  # 201 Created for POST

        data = response.json()
        assert data["name"] == "My Roster View"
        assert data["object_type"] == "roster"  # lowercase from StrEnum
        assert data["is_personal"] is True
        assert data["config"]["display_mode"] == "table"

    async def test_create_team_shared_view(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test POST /views/{object_type} creates a team-shared view."""
        view_data = {
            "name": "Team Campaigns View",
            "object_type": "campaigns",  # Must match path parameter
            "is_personal": False,
            "config": {
                "display_mode": "gallery",
                "column_filters": [],
                "column_visibility": {},
                "sorting": [{"id": "created_at", "desc": True}],
                "page_size": 20,
            },
        }

        response = await authenticated_client.post("/views/campaigns", json=view_data)
        assert response.status_code == 201  # 201 Created for POST

        data = response.json()
        assert data["name"] == "Team Campaigns View"
        assert data["is_personal"] is False
        assert data["user_id"] is None  # Team-shared views have no user_id
        assert data["config"]["display_mode"] == "gallery"

    async def test_list_views_for_object_type(
        self,
        authenticated_client: AsyncTestClient,
        team,
        user,
        db_session: AsyncSession,
    ):
        """Test GET /views?object_type=X returns personal and team views."""
        # Create personal view (mark as default to prevent system default from being added)
        personal_view = SavedView(
            name="My View",
            object_type=ObjectTypes.Roster,
            config={"display_mode": "table"},
            user_id=user.id,
            team_id=team.id,
            is_default=True,
        )
        db_session.add(personal_view)

        # Create team view
        team_view = SavedView(
            name="Team View",
            object_type=ObjectTypes.Roster,
            config={"display_mode": "gallery"},
            user_id=None,  # Team-shared
            team_id=team.id,
        )
        db_session.add(team_view)

        # Create view for different object type (should not appear)
        other_view = SavedView(
            name="Campaigns View",
            object_type=ObjectTypes.Campaigns,
            config={"display_mode": "card"},
            user_id=user.id,
            team_id=team.id,
        )
        db_session.add(other_view)

        await db_session.flush()
        await db_session.commit()  # Commit to ensure views are visible in other sessions

        # List views for Roster
        response = await authenticated_client.get("/views/roster")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2  # Personal + Team views, not Campaigns

        view_names = {v["name"] for v in data}
        assert "My View" in view_names
        assert "Team View" in view_names
        assert "Campaigns View" not in view_names

    async def test_get_view_by_id(
        self,
        authenticated_client: AsyncTestClient,
        team,
        user,
        db_session: AsyncSession,
    ):
        """Test GET /views/{object_type}/{id} returns view details."""
        view = SavedView(
            name="Test View",
            object_type=ObjectTypes.Roster,
            config={"display_mode": "table", "page_size": 50},
            user_id=user.id,
            team_id=team.id,
        )
        db_session.add(view)
        await db_session.flush()

        response = await authenticated_client.get(f"/views/roster/{sqid_encode(view.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(view.id)
        assert data["name"] == "Test View"
        assert data["config"]["page_size"] == 50

    async def test_update_personal_view(
        self,
        authenticated_client: AsyncTestClient,
        team,
        user,
        db_session: AsyncSession,
    ):
        """Test POST /views/{object_type}/{id} updates personal view."""
        view = SavedView(
            name="Original Name",
            object_type=ObjectTypes.Roster,
            config={"display_mode": "table"},
            user_id=user.id,
            team_id=team.id,
        )
        db_session.add(view)
        await db_session.flush()

        update_data = {
            "name": "Updated Name",
            "config": {
                "display_mode": "gallery",
                "column_filters": [{"id": "status", "value": "active"}],
                "column_visibility": {"email": False},
                "sorting": [],
                "page_size": 100,
            },
        }

        response = await authenticated_client.post(f"/views/roster/{sqid_encode(view.id)}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["config"]["display_mode"] == "gallery"
        assert data["config"]["page_size"] == 100

    async def test_cannot_update_others_personal_view(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test that users cannot update another user's personal view."""
        # Create another user
        from app.users.models import Role
        from tests.factories.users import UserFactory

        other_user = await UserFactory.create_async(session=db_session)
        role = Role(user_id=other_user.id, team_id=team.id, role_level="member")
        db_session.add(role)
        await db_session.flush()

        # Create view owned by other user
        other_view = SavedView(
            name="Other User's View",
            object_type=ObjectTypes.Roster,
            config={"display_mode": "table"},
            user_id=other_user.id,
            team_id=team.id,
        )
        db_session.add(other_view)
        await db_session.flush()

        # Try to update it (should fail)
        update_data = {"name": "Hacked Name"}
        response = await authenticated_client.post(f"/views/roster/{sqid_encode(other_view.id)}", json=update_data)
        assert response.status_code == 403

    async def test_cannot_update_team_shared_view(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test that team-shared views cannot be updated via POST."""
        team_view = SavedView(
            name="Team View",
            object_type=ObjectTypes.Campaigns,
            config={"display_mode": "card"},
            user_id=None,  # Team-shared
            team_id=team.id,
        )
        db_session.add(team_view)
        await db_session.flush()

        update_data = {"name": "New Name"}
        response = await authenticated_client.post(f"/views/campaigns/{sqid_encode(team_view.id)}", json=update_data)
        assert response.status_code == 403

    async def test_delete_personal_view(
        self,
        authenticated_client: AsyncTestClient,
        team,
        user,
        db_session: AsyncSession,
    ):
        """Test DELETE /views/{object_type}/{id} deletes personal view."""
        view = SavedView(
            name="View to Delete",
            object_type=ObjectTypes.Roster,
            config={"display_mode": "table"},
            user_id=user.id,
            team_id=team.id,
        )
        db_session.add(view)
        await db_session.flush()
        view_id = view.id

        response = await authenticated_client.delete(f"/views/roster/{sqid_encode(view_id)}")
        assert response.status_code == 204

        # Verify deletion
        stmt = select(SavedView).where(SavedView.id == view_id)
        result = await db_session.execute(stmt)
        deleted_view = result.scalar_one_or_none()
        assert deleted_view is None

    async def test_cannot_delete_others_personal_view(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test that users cannot delete another user's personal view."""
        # Create another user
        from app.users.models import Role
        from tests.factories.users import UserFactory

        other_user = await UserFactory.create_async(session=db_session)
        role = Role(user_id=other_user.id, team_id=team.id, role_level="member")
        db_session.add(role)
        await db_session.flush()

        # Create view owned by other user
        other_view = SavedView(
            name="Other User's View",
            object_type=ObjectTypes.Roster,
            config={"display_mode": "table"},
            user_id=other_user.id,
            team_id=team.id,
        )
        db_session.add(other_view)
        await db_session.flush()

        # Try to delete it (should fail)
        response = await authenticated_client.delete(f"/views/roster/{sqid_encode(other_view.id)}")
        assert response.status_code == 403

    async def test_cannot_delete_team_shared_view(
        self,
        authenticated_client: AsyncTestClient,
        team,
        db_session: AsyncSession,
    ):
        """Test that team-shared views cannot be deleted."""
        team_view = SavedView(
            name="Team View",
            object_type=ObjectTypes.Campaigns,
            config={"display_mode": "card"},
            user_id=None,  # Team-shared
            team_id=team.id,
        )
        db_session.add(team_view)
        await db_session.flush()

        response = await authenticated_client.delete(f"/views/campaigns/{sqid_encode(team_view.id)}")
        assert response.status_code == 403


class TestViewRLS:
    """Tests for Row-Level Security on views."""

    @pytest.mark.xfail(
        reason="RLS test fails in CI because postgres superuser bypasses RLS policies. "
        "Will be fixed when CI uses 'arive' user instead of 'postgres' user."
    )
    async def test_team_isolation(
        self,
        authenticated_client: AsyncTestClient,
        team,
        user,
        db_session: AsyncSession,
    ):
        """Test that users cannot see views from other teams."""
        # Create view for current team
        our_view = SavedView(
            name="Our View",
            object_type=ObjectTypes.Roster,
            config={"display_mode": "table"},
            user_id=user.id,
            team_id=team.id,
        )
        db_session.add(our_view)

        # Create another team and view
        from tests.factories.users import TeamFactory

        other_team = await TeamFactory.create_async(session=db_session)
        other_view = SavedView(
            name="Other Team View",
            object_type=ObjectTypes.Roster,
            config={"display_mode": "gallery"},
            user_id=None,  # Team-shared
            team_id=other_team.id,
        )
        db_session.add(other_view)
        await db_session.flush()
        await db_session.commit()  # Commit to ensure views are visible in other sessions

        # List views - should only see our team's views
        response = await authenticated_client.get("/views/roster")
        assert response.status_code == 200

        data = response.json()
        view_names = [v["name"] for v in data]
        assert "Our View" in view_names
        assert "Other Team View" not in view_names

        # Try to access other team's view directly (should fail via RLS)
        response = await authenticated_client.get(f"/views/roster/{sqid_encode(other_view.id)}")
        assert response.status_code == 404  # RLS blocks access
