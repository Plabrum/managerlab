"""Campaign-related model factories."""

from datetime import UTC, datetime

from polyfactory import Use

from app.campaigns.enums import CampaignStates
from app.campaigns.models import Campaign

from .base import BaseFactory


class CampaignFactory(BaseFactory):
    """Factory for creating Campaign instances."""

    __model__ = Campaign

    name = Use(BaseFactory.__faker__.catch_phrase)
    description = Use(BaseFactory.__faker__.text, max_nb_chars=500)
    state = CampaignStates.DRAFT
    assigned_roster_id = None  # Must be explicitly set if needed
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-1y",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))
    deleted_at = None
