import os
from typing import Any

import sqlalchemy as sa
from alembic_utils.pg_policy import PGPolicy
from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import BaseDBModel

# Global registry for RLS policies - consumed by alembic env.py
RLS_POLICY_REGISTRY: list[PGPolicy] = []


def RLSMixin(scope_with_campaign_id: bool = False) -> type:
    if scope_with_campaign_id:
        # Dual-scoped mixin: Has both team_id and campaign_id
        class _DualScopedMixin:
            team_id: Mapped[int] = mapped_column(
                sa.ForeignKey("teams.id", ondelete="RESTRICT"),
                nullable=False,
                index=True,
            )

            campaign_id: Mapped[int | None] = mapped_column(
                sa.ForeignKey("campaigns.id", ondelete="RESTRICT"),
                nullable=True,
                index=True,
            )

            def __init_subclass__(cls, **kwargs: Any) -> None:
                """Auto-register RLS policy and enablement when model class is defined."""
                super().__init_subclass__(**kwargs)

                # Only register if this is an actual table model (not the mixin itself)
                if not hasattr(cls, "__tablename__"):
                    return

                tablename: str = cls.__tablename__  # type: ignore[misc]

                # Register table for RLS enablement in metadata
                # This is used by the RLS comparator to detect when RLS needs to be enabled
                if "rls" not in BaseDBModel.metadata.info:
                    BaseDBModel.metadata.info["rls"] = set()
                BaseDBModel.metadata.info["rls"].add(tablename)

                # Create RLS policy for dual-scoped table
                # Check IS NOT NULL before casting to prevent errors
                policy = PGPolicy(
                    schema="public",
                    signature="dual_scope_policy",
                    on_entity=f"public.{tablename}",
                    definition="""
                        AS PERMISSIVE
                        FOR ALL
                        USING (
                            (current_setting('app.team_id', true) IS NOT NULL
                             AND team_id = current_setting('app.team_id', true)::int)
                            OR (current_setting('app.campaign_id', true) IS NOT NULL
                                AND campaign_id = current_setting('app.campaign_id', true)::int)
                            OR (current_setting('app.is_system_mode', true)::boolean IS TRUE)
                        )
                    """,
                )
                RLS_POLICY_REGISTRY.append(policy)

        return _DualScopedMixin

    else:

        class _TeamScopedMixin:
            team_id: Mapped[int] = mapped_column(
                sa.ForeignKey("teams.id", ondelete="RESTRICT"),
                nullable=False,
                index=True,
            )

            def __init_subclass__(cls, **kwargs: Any) -> None:
                """Auto-register RLS policy and enablement when model class is defined."""
                super().__init_subclass__(**kwargs)

                # Only register if this is an actual table model (not the mixin itself)
                if not hasattr(cls, "__tablename__"):
                    return

                tablename: str = cls.__tablename__  # type: ignore[misc]

                # Register table for RLS enablement in metadata
                # This is used by the RLS comparator to detect when RLS needs to be enabled
                if "rls" not in BaseDBModel.metadata.info:
                    BaseDBModel.metadata.info["rls"] = set()
                BaseDBModel.metadata.info["rls"].add(tablename)

                # Create RLS policy for team-scoped table
                # Check IS NOT NULL before casting to prevent errors
                policy = PGPolicy(
                    schema="public",
                    signature="team_scope_policy",
                    on_entity=f"public.{tablename}",
                    definition="""
                        AS PERMISSIVE
                        FOR ALL
                        USING (
                            (current_setting('app.team_id', true) IS NOT NULL
                             AND team_id = current_setting('app.team_id', true)::int)
                            OR current_setting('app.is_system_mode', true)::boolean IS TRUE
                        )
                    """,
                )
                RLS_POLICY_REGISTRY.append(policy)

        return _TeamScopedMixin
