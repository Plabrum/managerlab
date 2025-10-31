"""Brand-related model factories."""

from datetime import UTC, datetime

from polyfactory import Use

from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact

from .base import BaseFactory


class BrandFactory(BaseFactory):
    """Factory for creating Brand instances."""

    __model__ = Brand

    name = Use(BaseFactory.__faker__.company)
    description = Use(BaseFactory.__faker__.text, max_nb_chars=500)
    tone_of_voice = Use(
        BaseFactory.__faker__.random_element,
        elements=(
            "Professional and authoritative",
            "Friendly and approachable",
            "Casual and conversational",
            "Energetic and enthusiastic",
            "Sophisticated and elegant",
        ),
    )
    brand_values = Use(BaseFactory.__faker__.text, max_nb_chars=300)
    target_audience = Use(
        BaseFactory.__faker__.random_element,
        elements=(
            "Young professionals (25-35)",
            "Parents with children",
            "Small business owners",
            "Tech enthusiasts",
            "Health-conscious consumers",
            "Luxury shoppers",
        ),
    )
    website = Use(BaseFactory.__faker__.url)
    email = Use(BaseFactory.__faker__.company_email)
    phone = Use(BaseFactory.__faker__.phone_number)
    notes = Use(BaseFactory.__faker__.text, max_nb_chars=200)
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-2y",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))


class BrandContactFactory(BaseFactory):
    """Factory for creating BrandContact instances."""

    __model__ = BrandContact

    first_name = Use(BaseFactory.__faker__.first_name)
    last_name = Use(BaseFactory.__faker__.last_name)
    email = Use(BaseFactory.__faker__.email)
    phone = Use(BaseFactory.__faker__.phone_number)
    notes = Use(BaseFactory.__faker__.text, max_nb_chars=150)
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-1y",
        end_date="now",
        tzinfo=UTC,
    )
    updated_at = Use(lambda: datetime.now(tz=UTC))
