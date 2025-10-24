"""User-related model factories."""

from datetime import datetime, timezone

from polyfactory import Use

from app.users.models import User, WaitlistEntry, Team, Role
from app.users.enums import UserStates, RoleLevel
from app.roster.models import Roster
from app.roster.enums import RosterStates
from .base import BaseFactory


class UserFactory(BaseFactory):
    """Factory for creating User instances."""

    __model__ = User

    name = Use(BaseFactory.__faker__.name)
    email = Use(BaseFactory.__faker__.email)
    email_verified = Use(BaseFactory.__faker__.boolean, chance_of_getting_true=80)
    state = UserStates.ACTIVE
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-1y",
        end_date="now",
        tzinfo=timezone.utc,
    )
    updated_at = Use(lambda: datetime.now(tz=timezone.utc))


class TeamFactory(BaseFactory):
    """Factory for creating Team instances."""

    __model__ = Team

    name = Use(BaseFactory.__faker__.company)
    description = Use(BaseFactory.__faker__.catch_phrase)
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-1y",
        end_date="now",
        tzinfo=timezone.utc,
    )
    updated_at = Use(lambda: datetime.now(tz=timezone.utc))


class RoleFactory(BaseFactory):
    """Factory for creating Role instances."""

    __model__ = Role

    role_level = RoleLevel.MEMBER
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-1y",
        end_date="now",
        tzinfo=timezone.utc,
    )
    updated_at = Use(lambda: datetime.now(tz=timezone.utc))


class RosterFactory(BaseFactory):
    """Factory for creating RosterMember instances."""

    __model__ = Roster

    name = Use(BaseFactory.__faker__.name)
    email = Use(BaseFactory.__faker__.email)
    phone = Use(BaseFactory.__faker__.phone_number)
    instagram_handle = Use(lambda: f"@{BaseFactory.__faker__.user_name()}")
    state = RosterStates.ACTIVE
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-1y",
        end_date="now",
        tzinfo=timezone.utc,
    )
    updated_at = Use(lambda: datetime.now(tz=timezone.utc))


class WaitlistEntryFactory(BaseFactory):
    """Factory for creating WaitlistEntry instances."""

    __model__ = WaitlistEntry

    name = Use(BaseFactory.__faker__.name)
    email = Use(BaseFactory.__faker__.email)
    company = Use(BaseFactory.__faker__.company)
    message = Use(BaseFactory.__faker__.text, max_nb_chars=200)
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-6m",
        end_date="now",
        tzinfo=timezone.utc,
    )
    updated_at = Use(lambda: datetime.now(tz=timezone.utc))
