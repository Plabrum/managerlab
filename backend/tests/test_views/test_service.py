"""Tests for views service layer functions."""

import pytest
from litestar.exceptions import PermissionDeniedException

from app.objects.enums import ObjectTypes
from app.views.models import SavedView
from app.views.services import (
    check_view_ownership,
    clear_user_defaults,
    get_or_create_default_view,
)

pytestmark = pytest.mark.asyncio


# Test check_view_ownership
async def test_check_view_ownership_allows_owner():
    """Test check_view_ownership passes for owner."""
    view = SavedView(
        id=1,
        name="Test View",
        object_type=ObjectTypes.Campaigns,
        config={},
        user_id=123,  # Personal view (is_personal computed from user_id)
        team_id=1,
    )

    # Should not raise
    check_view_ownership(view, user_id=123)


async def test_check_view_ownership_denies_non_owner():
    """Test check_view_ownership raises for non-owner."""
    view = SavedView(
        id=1,
        name="Test View",
        object_type=ObjectTypes.Campaigns,
        config={},
        user_id=123,  # Personal view owned by user 123
        team_id=1,
    )

    with pytest.raises(PermissionDeniedException, match="You can only modify your own personal views"):
        check_view_ownership(view, user_id=456)


async def test_check_view_ownership_denies_team_shared():
    """Test check_view_ownership raises for team-shared views."""
    view = SavedView(
        id=1,
        name="Test View",
        object_type=ObjectTypes.Campaigns,
        config={},
        user_id=None,  # Team-shared (is_team_shared computed from user_id=None)
        team_id=1,
    )

    with pytest.raises(PermissionDeniedException, match="Team-shared views cannot be modified"):
        check_view_ownership(view, user_id=123)


async def test_check_view_ownership_simple_message():
    """Test check_view_ownership has simple error messages."""
    view = SavedView(
        id=1,
        name="Test View",
        object_type=ObjectTypes.Campaigns,
        config={},
        user_id=None,  # Team-shared
        team_id=1,
    )

    with pytest.raises(PermissionDeniedException, match="Team-shared views cannot be modified"):
        check_view_ownership(view, user_id=123)


# Test clear_user_defaults
async def test_clear_user_defaults(db_session, team, user):
    """Test clear_user_defaults unsets is_default flag."""
    # Create a default view for Campaigns
    view1 = SavedView(
        name="Default Campaigns View",
        object_type=ObjectTypes.Campaigns,
        config={"display_mode": "table"},
        user_id=user.id,
        team_id=team.id,
        is_default=True,
    )
    # Create a default view for different object type (should not be affected)
    view2 = SavedView(
        name="Default Deliverables View",
        object_type=ObjectTypes.Deliverables,
        config={"display_mode": "table"},
        user_id=user.id,
        team_id=team.id,
        is_default=True,
    )

    db_session.add_all([view1, view2])
    await db_session.flush()

    # Clear Campaigns defaults
    await clear_user_defaults(db_session, user_id=user.id, object_type=ObjectTypes.Campaigns)

    await db_session.refresh(view1)
    await db_session.refresh(view2)

    assert view1.is_default is False  # Campaigns default was cleared
    assert view2.is_default is True  # Different object type, not affected


# Test get_or_create_default_view
async def test_get_or_create_default_view_returns_saved(db_session, team, user):
    """Test returns saved default when it exists."""
    view = SavedView(
        name="My Default",
        object_type=ObjectTypes.Campaigns,
        config={"display_mode": "table"},
        user_id=user.id,  # Personal view
        team_id=team.id,
        is_default=True,
    )
    db_session.add(view)
    await db_session.flush()
    await db_session.refresh(view)

    result = await get_or_create_default_view(db_session, user_id=user.id, object_type=ObjectTypes.Campaigns)

    assert result.id == view.id
    assert result.name == "My Default"
    assert result.is_default is True


async def test_get_or_create_default_view_returns_fallback(db_session):
    """Test returns hard-coded default when no saved default exists."""
    result = await get_or_create_default_view(db_session, user_id=999, object_type=ObjectTypes.Campaigns)

    assert result.id is None  # Hard-coded default
    assert result.name == "Default campaigns View"
    assert result.is_default is True
    assert result.is_personal is False
    assert result.user_id is None
    assert result.team_id is None


async def test_get_or_create_default_view_ignores_non_default(db_session, team, user):
    """Test ignores non-default saved views."""
    # Create a non-default view
    view = SavedView(
        name="Not Default",
        object_type=ObjectTypes.Campaigns,
        config={"display_mode": "table"},
        user_id=user.id,  # Personal view
        team_id=team.id,
        is_default=False,  # Not default
    )
    db_session.add(view)
    await db_session.flush()

    result = await get_or_create_default_view(db_session, user_id=user.id, object_type=ObjectTypes.Campaigns)

    # Should return hard-coded default, not the non-default saved view
    assert result.id is None
    assert result.name == "Default campaigns View"
