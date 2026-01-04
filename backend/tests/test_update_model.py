"""Tests for update_model utility with nested object handling."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.addresses.models import Address
from app.addresses.schemas import AddressCreateSchema
from app.events.enums import EventType
from app.events.models import Event
from app.roster.schemas import RosterUpdateSchema
from app.utils.db import update_model
from tests.factories.users import RosterFactory


class TestUpdateModelNestedObjects:
    """Tests for update_model handling of nested objects."""

    async def test_update_simple_fields(
        self,
        db_session: AsyncSession,
        team,
        user,
    ):
        """Test update_model updates simple fields correctly."""
        # Create a roster member
        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=team.id,
            user_id=user.id,
            name="Original Name",
            email="original@example.com",
            profile_photo_id=None,
        )
        await db_session.flush()

        # Update simple fields
        update_data = RosterUpdateSchema(
            name="Updated Name",
            email="updated@example.com",
            phone=None,
            birthdate=None,
            gender=None,
            address=None,
            instagram_handle=None,
            facebook_handle=None,
            tiktok_handle=None,
            youtube_channel=None,
            profile_photo_id=None,
        )

        await update_model(
            session=db_session,
            model_instance=roster,
            update_vals=update_data,
            user_id=user.id,
            team_id=team.id,
        )

        await db_session.refresh(roster)
        assert roster.name == "Updated Name"
        assert roster.email == "updated@example.com"

    async def test_update_existing_nested_object(
        self,
        db_session: AsyncSession,
        team,
        user,
    ):
        """Test update_model updates existing nested address object."""
        # Create address
        address = Address(
            team_id=team.id,
            address1="123 Old St",
            city="Old City",
            country="US",
        )
        db_session.add(address)
        await db_session.flush()

        # Create roster with address
        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=team.id,
            user_id=user.id,
            address_id=address.id,
            profile_photo_id=None,
        )
        await db_session.flush()

        # Update with new address data (should update existing address)
        update_data = RosterUpdateSchema(
            name=roster.name,
            email=roster.email,
            phone=roster.phone,
            birthdate=roster.birthdate,
            gender=roster.gender,
            address=AddressCreateSchema(
                address1="456 New St",
                city="New City",
                country="US",
            ),
            instagram_handle=roster.instagram_handle,
            facebook_handle=roster.facebook_handle,
            tiktok_handle=roster.tiktok_handle,
            youtube_channel=roster.youtube_channel,
            profile_photo_id=None,
        )

        await update_model(
            session=db_session,
            model_instance=roster,
            update_vals=update_data,
            user_id=user.id,
            team_id=team.id,
        )

        await db_session.refresh(roster)
        await db_session.refresh(address)

        # Address should be updated, not replaced
        assert roster.address_id == address.id
        assert address.address1 == "456 New St"
        assert address.city == "New City"

    async def test_clear_nested_object(
        self,
        db_session: AsyncSession,
        team,
        user,
    ):
        """Test update_model clears nested object when set to None."""
        # Create address
        address = Address(
            team_id=team.id,
            address1="123 Old St",
            city="Old City",
            country="US",
        )
        db_session.add(address)
        await db_session.flush()

        # Create roster with address
        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=team.id,
            user_id=user.id,
            address_id=address.id,
            profile_photo_id=None,
        )
        await db_session.flush()

        # Update with address=None (should clear the relationship)
        update_data = RosterUpdateSchema(
            name=roster.name,
            email=roster.email,
            phone=roster.phone,
            birthdate=roster.birthdate,
            gender=roster.gender,
            address=None,
            instagram_handle=roster.instagram_handle,
            facebook_handle=roster.facebook_handle,
            tiktok_handle=roster.tiktok_handle,
            youtube_channel=roster.youtube_channel,
            profile_photo_id=None,
        )

        await update_model(
            session=db_session,
            model_instance=roster,
            update_vals=update_data,
            user_id=user.id,
            team_id=team.id,
        )

        await db_session.refresh(roster)

        # Address should be cleared
        assert roster.address_id is None

    async def test_update_emits_events(
        self,
        db_session: AsyncSession,
        team,
        user,
    ):
        """Test update_model emits UPDATED events for changed fields."""
        # Create a roster member
        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=team.id,
            user_id=user.id,
            name="Original Name",
            email="original@example.com",
            profile_photo_id=None,
        )
        await db_session.flush()

        # Count events before update
        from sqlalchemy import func, select

        count_before = await db_session.scalar(
            select(func.count())
            .select_from(Event)
            .where(Event.object_id == roster.id)
            .where(Event.object_type == "roster")
        )

        # Update fields
        update_data = RosterUpdateSchema(
            name="Updated Name",
            email="updated@example.com",
            phone=None,
            birthdate=None,
            gender=None,
            address=None,
            instagram_handle=None,
            facebook_handle=None,
            tiktok_handle=None,
            youtube_channel=None,
            profile_photo_id=None,
        )

        await update_model(
            session=db_session,
            model_instance=roster,
            update_vals=update_data,
            user_id=user.id,
            team_id=team.id,
        )

        await db_session.flush()

        # Should have emitted an UPDATED event
        count_after = await db_session.scalar(
            select(func.count())
            .select_from(Event)
            .where(Event.object_id == roster.id)
            .where(Event.object_type == "roster")
        )

        assert count_after is not None and count_before is not None
        assert count_after > count_before

        # Verify the event has correct data
        event = await db_session.scalar(
            select(Event)
            .where(Event.object_id == roster.id)
            .where(Event.object_type == "roster")
            .where(Event.event_type == EventType.UPDATED)
            .order_by(Event.created_at.desc())
        )

        assert event is not None
        assert event.actor_id == user.id
        assert event.event_data is not None
        assert "changes" in event.event_data

    async def test_update_no_event_when_tracking_disabled(
        self,
        db_session: AsyncSession,
        team,
        user,
    ):
        """Test update_model doesn't emit events when should_track=False."""
        # Create a roster member
        roster = await RosterFactory.create_async(
            session=db_session,
            team_id=team.id,
            user_id=user.id,
            name="Original Name",
            profile_photo_id=None,
        )
        await db_session.flush()

        # Count events before update
        from sqlalchemy import func, select

        count_before = await db_session.scalar(
            select(func.count())
            .select_from(Event)
            .where(Event.object_id == roster.id)
            .where(Event.object_type == "roster")
        )

        # Update with tracking disabled
        update_data = RosterUpdateSchema(
            name="Updated Name",
            email=None,
            phone=None,
            birthdate=None,
            gender=None,
            address=None,
            instagram_handle=None,
            facebook_handle=None,
            tiktok_handle=None,
            youtube_channel=None,
            profile_photo_id=None,
        )

        await update_model(
            session=db_session,
            model_instance=roster,
            update_vals=update_data,
            user_id=user.id,
            team_id=team.id,
            should_track=False,  # Disable event tracking
        )

        await db_session.flush()

        # Should NOT have emitted an event
        count_after = await db_session.scalar(
            select(func.count())
            .select_from(Event)
            .where(Event.object_id == roster.id)
            .where(Event.object_type == "roster")
        )

        assert count_after == count_before
