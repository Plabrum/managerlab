from typing import Type, Any
import os
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from alembic_utils.pg_policy import PGPolicy

# Global registry for RLS policies - consumed by alembic env.py
RLS_POLICY_REGISTRY: list[PGPolicy] = []

# Flag to disable policy registration during migration generation
REGISTER_POLICIES = os.getenv("REGISTER_RLS_POLICIES", "true").lower() == "true"


def RLSMixin(scope_with_campaign_id: bool = False) -> Type:
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
                """Auto-register RLS policy when model class is defined."""
                super().__init_subclass__(**kwargs)

                # Only register if this is an actual table model and policies are enabled
                if REGISTER_POLICIES and hasattr(cls, "__tablename__"):
                    # Create RLS policy for dual-scoped table
                    policy = PGPolicy(
                        schema="public",
                        signature="dual_scope_policy",
                        on_entity=f"public.{getattr(cls, '__tablename__')}",
                        definition="""
                            AS PERMISSIVE
                            FOR ALL
                            USING (
                                (team_id = current_setting('app.team_id', true)::int)
                                OR (campaign_id = current_setting('app.campaign_id', true)::int)
                                OR (current_setting('app.team_id', true) IS NULL
                                    AND current_setting('app.campaign_id', true) IS NULL)
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
                """Auto-register RLS policy when model class is defined."""
                super().__init_subclass__(**kwargs)

                # Only register if this is an actual table model and policies are enabled
                if REGISTER_POLICIES and hasattr(cls, "__tablename__"):
                    # Create RLS policy for team-scoped table
                    policy = PGPolicy(
                        schema="public",
                        signature="team_scope_policy",
                        on_entity=f"public.{getattr(cls, '__tablename__')}",
                        definition="""
                            AS PERMISSIVE
                            FOR ALL
                            USING (
                                team_id = current_setting('app.team_id', true)::int
                                OR current_setting('app.team_id', true) IS NULL
                            )
                        """,
                    )
                    RLS_POLICY_REGISTRY.append(policy)

        return _TeamScopedMixin
