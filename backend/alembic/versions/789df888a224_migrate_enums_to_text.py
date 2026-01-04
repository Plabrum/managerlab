"""migrate_enums_to_text

Revision ID: 789df888a224
Revises: 6416d060aa23
Create Date: 2026-01-04 01:46:03.725703

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "789df888a224"
down_revision: str | Sequence[str] | None = "6416d060aa23"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Migrate PostgreSQL ENUM types to TEXT columns.

    This migration converts all PostgreSQL native ENUM types to TEXT columns,
    which allows for easier schema evolution and enables case-insensitive queries.
    The TextEnum SQLAlchemy type decorator will handle conversion between Python
    enums and TEXT values.

    Enum values are already stored as uppercase names (e.g., 'FLAT_FEE', 'INSTAGRAM')
    which matches the TextEnum storage format, so no data transformation is needed.
    """

    # 1. Convert addresses.address_type (addresstype -> TEXT)
    op.execute("""
        ALTER TABLE addresses
        ALTER COLUMN address_type TYPE TEXT
        USING address_type::text
    """)

    # 2. Convert campaigns.compensation_structure (compensationstructure -> TEXT)
    op.execute("""
        ALTER TABLE campaigns
        ALTER COLUMN compensation_structure TYPE TEXT
        USING compensation_structure::text
    """)

    # 3. Convert campaigns.counterparty_type (counterpartytype -> TEXT)
    op.execute("""
        ALTER TABLE campaigns
        ALTER COLUMN counterparty_type TYPE TEXT
        USING counterparty_type::text
    """)

    # 4. Convert campaigns.ownership_mode (ownershipmode -> TEXT)
    op.execute("""
        ALTER TABLE campaigns
        ALTER COLUMN ownership_mode TYPE TEXT
        USING ownership_mode::text
    """)

    # 5. Convert deliverables.deliverable_type (deliverabletype -> TEXT)
    op.execute("""
        ALTER TABLE deliverables
        ALTER COLUMN deliverable_type TYPE TEXT
        USING deliverable_type::text
    """)

    # 6. Convert deliverables.platforms (socialmediaplatforms -> TEXT)
    op.execute("""
        ALTER TABLE deliverables
        ALTER COLUMN platforms TYPE TEXT
        USING platforms::text
    """)

    # 7. Convert events.event_type (eventtype -> TEXT)
    op.execute("""
        ALTER TABLE events
        ALTER COLUMN event_type TYPE TEXT
        USING event_type::text
    """)

    # 8. Drop the now-unused PostgreSQL ENUM types
    # Note: We need to drop them in order to avoid dependency issues
    op.execute("DROP TYPE IF EXISTS addresstype")
    op.execute("DROP TYPE IF EXISTS compensationstructure")
    op.execute("DROP TYPE IF EXISTS counterpartytype")
    op.execute("DROP TYPE IF EXISTS deliverabletype")
    op.execute("DROP TYPE IF EXISTS eventtype")
    op.execute("DROP TYPE IF EXISTS object_types")  # May not be in use, but drop if exists
    op.execute("DROP TYPE IF EXISTS ownershipmode")
    op.execute("DROP TYPE IF EXISTS socialmediaplatforms")


def downgrade() -> None:
    """Downgrade schema - recreate PostgreSQL ENUM types.

    Note: This downgrade recreates the ENUM types based on the current enum values
    in the Python code. If enum values have changed since this migration, you may
    need to adjust this downgrade script.
    """

    # 1. Recreate the ENUM types
    op.execute("""
        CREATE TYPE addresstype AS ENUM ('HOME', 'WORK', 'OTHER')
    """)

    op.execute("""
        CREATE TYPE compensationstructure AS ENUM ('FLAT_FEE', 'PER_DELIVERABLE', 'PERFORMANCE_BASED')
    """)

    op.execute("""
        CREATE TYPE counterpartytype AS ENUM ('AGENCY', 'BRAND')
    """)

    op.execute("""
        CREATE TYPE ownershipmode AS ENUM ('BRAND_OWNED', 'CREATOR_OWNED', 'SHARED')
    """)

    op.execute("""
        CREATE TYPE deliverabletype AS ENUM (
            'INSTAGRAM_FEED_POST', 'INSTAGRAM_STORY_FRAME', 'INSTAGRAM_REEL', 'INSTAGRAM_CAROUSEL',
            'TIKTOK_VIDEO', 'TIKTOK_PHOTO_POST',
            'YOUTUBE_VIDEO', 'YOUTUBE_SHORT', 'YOUTUBE_COMMUNITY_POST',
            'FACEBOOK_POST', 'FACEBOOK_STORY', 'FACEBOOK_REEL',
            'BLOG_POST', 'PODCAST_EPISODE', 'EMAIL_NEWSLETTER'
        )
    """)

    op.execute("""
        CREATE TYPE socialmediaplatforms AS ENUM ('INSTAGRAM', 'FACEBOOK', 'TIKTOK', 'YOUTUBE')
    """)

    op.execute("""
        CREATE TYPE eventtype AS ENUM ('CREATED', 'UPDATED', 'DELETED', 'STATE_CHANGED', 'CUSTOM')
    """)

    # 2. Convert columns back to ENUM types
    op.execute("""
        ALTER TABLE addresses
        ALTER COLUMN address_type TYPE addresstype
        USING address_type::addresstype
    """)

    op.execute("""
        ALTER TABLE campaigns
        ALTER COLUMN compensation_structure TYPE compensationstructure
        USING compensation_structure::compensationstructure
    """)

    op.execute("""
        ALTER TABLE campaigns
        ALTER COLUMN counterparty_type TYPE counterpartytype
        USING counterparty_type::counterpartytype
    """)

    op.execute("""
        ALTER TABLE campaigns
        ALTER COLUMN ownership_mode TYPE ownershipmode
        USING ownership_mode::ownershipmode
    """)

    op.execute("""
        ALTER TABLE deliverables
        ALTER COLUMN deliverable_type TYPE deliverabletype
        USING deliverable_type::deliverabletype
    """)

    op.execute("""
        ALTER TABLE deliverables
        ALTER COLUMN platforms TYPE socialmediaplatforms
        USING platforms::socialmediaplatforms
    """)

    op.execute("""
        ALTER TABLE events
        ALTER COLUMN event_type TYPE eventtype
        USING event_type::eventtype
    """)

    # Note: object_types is not recreated as it appears to be unused
