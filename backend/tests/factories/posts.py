"""Post-related model factories."""

from datetime import datetime, timezone

from polyfactory import Use

from app.posts.models import Post
from app.posts.enums import PostStates, SocialMediaPlatforms, CompensationStructure
from .base import BaseFactory


class PostFactory(BaseFactory):
    """Factory for creating Post instances."""

    __model__ = Post

    title = Use(BaseFactory.__faker__.sentence, nb_words=6)
    content = Use(BaseFactory.__faker__.text, max_nb_chars=2000)
    platforms = Use(
        BaseFactory.__faker__.random_element, elements=list(SocialMediaPlatforms)
    )
    posting_date = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="+0d",
        end_date="+30d",
        tzinfo=timezone.utc,
    )
    notes = Use(
        lambda: {
            "hashtags": BaseFactory.__faker__.words(nb=5),
            "mentions": BaseFactory.__faker__.words(nb=2),
        }
    )
    compensation_structure = Use(
        BaseFactory.__faker__.random_element, elements=list(CompensationStructure)
    )
    state = PostStates.DRAFT
    created_at = Use(
        BaseFactory.__faker__.date_time_between,
        start_date="-3m",
        end_date="now",
        tzinfo=timezone.utc,
    )
    updated_at = Use(lambda: datetime.now(tz=timezone.utc))
