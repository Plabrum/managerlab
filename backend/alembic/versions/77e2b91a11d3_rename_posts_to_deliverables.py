"""rename posts to deliverables

Revision ID: 77e2b91a11d3
Revises: 56ef7b94a04f
Create Date: 2025-10-20 23:17:07.468585

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "77e2b91a11d3"
down_revision: str | Sequence[str] | None = "56ef7b94a04f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - rename posts to deliverables."""
    # Step 1: Drop FK constraints from association table that depend on posts table
    op.drop_constraint("post_media_post_id_fkey", "post_media", type_="foreignkey")
    op.drop_constraint("post_media_media_id_fkey", "post_media", type_="foreignkey")

    # Step 2: Drop primary key from association table
    op.drop_constraint("post_media_pkey", "post_media", type_="primary")

    # Step 3: Rename the column in the association table
    op.alter_column("post_media", "post_id", new_column_name="deliverable_id")

    # Step 4: Rename the association table
    op.rename_table("post_media", "deliverable_media")

    # Step 5: Rename the main table (this is safe now since FK constraints are dropped)
    op.rename_table("posts", "deliverables")

    # Step 6: Drop old indexes from main table
    op.drop_index("ix_posts_campaign_id", table_name="deliverables")
    op.drop_index("ix_posts_deleted_at", table_name="deliverables")
    op.drop_index("ix_posts_state", table_name="deliverables")
    op.drop_index("ix_posts_team_id", table_name="deliverables")

    # Step 7: Drop old FK and PK constraints from main table
    op.drop_constraint("posts_campaign_id_fkey", "deliverables", type_="foreignkey")
    op.drop_constraint("posts_team_id_fkey", "deliverables", type_="foreignkey")
    op.drop_constraint("posts_pkey", "deliverables", type_="primary")

    # Step 8: Create new constraints on main table with new names
    op.create_primary_key("deliverables_pkey", "deliverables", ["id"])
    op.create_foreign_key(
        "deliverables_campaign_id_fkey",
        "deliverables",
        "campaigns",
        ["campaign_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "deliverables_team_id_fkey",
        "deliverables",
        "teams",
        ["team_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # Step 9: Create new indexes on main table
    op.create_index(
        op.f("ix_deliverables_campaign_id"),
        "deliverables",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(op.f("ix_deliverables_deleted_at"), "deliverables", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_deliverables_state"), "deliverables", ["state"], unique=False)
    op.create_index(op.f("ix_deliverables_team_id"), "deliverables", ["team_id"], unique=False)

    # Step 10: Re-create constraints on association table
    op.create_primary_key("deliverable_media_pkey", "deliverable_media", ["deliverable_id", "media_id"])
    op.create_foreign_key(
        "deliverable_media_deliverable_id_fkey",
        "deliverable_media",
        "deliverables",
        ["deliverable_id"],
        ["id"],
    )
    op.create_foreign_key(
        "deliverable_media_media_id_fkey",
        "deliverable_media",
        "media",
        ["media_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema - rename deliverables back to posts."""
    # Reverse the upgrade process in reverse order

    # Step 1: Drop FK constraints from association table
    op.drop_constraint("deliverable_media_media_id_fkey", "deliverable_media", type_="foreignkey")
    op.drop_constraint("deliverable_media_deliverable_id_fkey", "deliverable_media", type_="foreignkey")

    # Step 2: Drop primary key from association table
    op.drop_constraint("deliverable_media_pkey", "deliverable_media", type_="primary")

    # Step 3: Drop indexes from main table
    op.drop_index(op.f("ix_deliverables_team_id"), table_name="deliverables")
    op.drop_index(op.f("ix_deliverables_state"), table_name="deliverables")
    op.drop_index(op.f("ix_deliverables_deleted_at"), table_name="deliverables")
    op.drop_index(op.f("ix_deliverables_campaign_id"), table_name="deliverables")

    # Step 4: Drop FK and PK constraints from main table
    op.drop_constraint("deliverables_team_id_fkey", "deliverables", type_="foreignkey")
    op.drop_constraint("deliverables_campaign_id_fkey", "deliverables", type_="foreignkey")
    op.drop_constraint("deliverables_pkey", "deliverables", type_="primary")

    # Step 5: Rename main table back
    op.rename_table("deliverables", "posts")

    # Step 6: Rename association table back
    op.rename_table("deliverable_media", "post_media")

    # Step 7: Rename column back in association table
    op.alter_column("post_media", "deliverable_id", new_column_name="post_id")

    # Step 8: Re-create old constraints on main table
    op.create_primary_key("posts_pkey", "posts", ["id"])
    op.create_foreign_key(
        "posts_campaign_id_fkey",
        "posts",
        "campaigns",
        ["campaign_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key("posts_team_id_fkey", "posts", "teams", ["team_id"], ["id"], ondelete="RESTRICT")

    # Step 9: Re-create old indexes on main table
    op.create_index("ix_posts_campaign_id", "posts", ["campaign_id"], unique=False)
    op.create_index("ix_posts_deleted_at", "posts", ["deleted_at"], unique=False)
    op.create_index("ix_posts_state", "posts", ["state"], unique=False)
    op.create_index("ix_posts_team_id", "posts", ["team_id"], unique=False)

    # Step 10: Re-create old constraints on association table
    op.create_primary_key("post_media_pkey", "post_media", ["post_id", "media_id"])
    op.create_foreign_key("post_media_post_id_fkey", "post_media", "posts", ["post_id"], ["id"])
    op.create_foreign_key("post_media_media_id_fkey", "post_media", "media", ["media_id"], ["id"])
