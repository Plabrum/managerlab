"""Deliverable-related model factories."""

from datetime import UTC, datetime

from polyfactory import Use

from app.campaigns.enums import CompensationStructure
from app.deliverables.enums import (
    DeliverableStates,
    SocialMediaPlatforms,
)
from app.deliverables.models import Deliverable

from .base import BaseFactory


class DeliverableFactory(BaseFactory):
    """Factory for creating Deliverable instances."""

    __model__ = Deliverable

    title = Use(BaseFactory.__faker__.sentence, nb_words=6)
    content = Use(BaseFactory.__faker__.text, max_nb_chars=2000)
    platforms = Use(BaseFactory.__faker__.random_element, elements=list(SocialMediaPlatforms))
    posting_date = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="+0d",
        end_date="+30d",
        tzinfo=UTC,
    )
    notes = Use(
        lambda: {
            "hashtags": BaseFactory.__faker__.words(nb=5),
            "mentions": BaseFactory.__faker__.words(nb=2),
        }
    )
    compensation_structure = Use(BaseFactory.__faker__.random_element, elements=list(CompensationStructure))
    state = DeliverableStates.DRAFT
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-3m",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))
