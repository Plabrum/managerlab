from decimal import Decimal
from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.campaigns.enums import (
    CampaignStates,
    CampaignGuestAccessLevel,
    CompensationStructure,
    CounterpartyType,
    OwnershipMode,
)
from app.state_machine.models import StateMachineMixin

if TYPE_CHECKING:
    from app.deliverables.models import Deliverable
    from app.brands.models.brands import Brand
    from app.brands.models.contacts import BrandContact
    from app.payments.models import Invoice
    from app.users.models import User, Roster


class Campaign(
    RLSMixin(),
    StateMachineMixin(
        state_enum=CampaignStates,
        initial_state=CampaignStates.DRAFT,
    ),
    BaseDBModel,
):
    __tablename__ = "campaigns"

    # Basic info
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Counterparty information
    counterparty_type: Mapped[CounterpartyType | None] = mapped_column(
        sa.Enum(CounterpartyType), nullable=True
    )
    counterparty_name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    counterparty_email: Mapped[str | None] = mapped_column(
        sa.String(255), nullable=True
    )

    # Compensation
    compensation_structure: Mapped[CompensationStructure | None] = mapped_column(
        sa.Enum(CompensationStructure), nullable=True
    )
    compensation_total_usd: Mapped[float | None] = mapped_column(
        sa.Float, nullable=True
    )
    payment_terms_days: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, default=30
    )

    # Flight window
    flight_start_date: Mapped[sa.Date | None] = mapped_column(sa.Date, nullable=True)
    flight_end_date: Mapped[sa.Date | None] = mapped_column(sa.Date, nullable=True)

    # FTC & Usage Rights
    ftc_string: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    usage_duration: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    usage_territory: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    usage_paid_media_option: Mapped[bool | None] = mapped_column(
        sa.Boolean, nullable=True, default=False
    )

    # Exclusivity
    exclusivity_category: Mapped[str | None] = mapped_column(
        sa.String(128), nullable=True
    )
    exclusivity_days_before: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, default=0
    )
    exclusivity_days_after: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, default=0
    )

    # Ownership
    ownership_mode: Mapped[OwnershipMode | None] = mapped_column(
        sa.Enum(OwnershipMode), nullable=True, default=OwnershipMode.BRAND_OWNED
    )

    # Global approval settings
    approval_rounds: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, default=1
    )
    approval_sla_hours: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True, default=48
    )

    # Foreign keys - Campaign always has a Brand
    assigned_roster_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("roster.id"), nullable=True
    )
    brand_id: Mapped[int] = mapped_column(sa.ForeignKey("brands.id"), nullable=False)

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="campaigns")
    assigned_roster: Mapped["Roster | None"] = relationship(
        "Roster",
        back_populates="campaigns",
        primaryjoin="Campaign.assigned_roster_id == Roster.id",
        foreign_keys="Campaign.assigned_roster_id",
    )
    deliverables: Mapped[list["Deliverable"]] = relationship(
        "Deliverable", back_populates="campaign"
    )
    lead_contacts: Mapped[list["BrandContact"]] = relationship(
        "BrandContact",
        secondary="campaign_lead_contacts",
        back_populates="campaigns_as_lead",
    )
    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice", back_populates="campaign"
    )
    payment_blocks: Mapped[list["PaymentBlock"]] = relationship(
        "PaymentBlock",
        back_populates="campaign",
        cascade="all, delete-orphan",
        order_by="PaymentBlock.order_index",
    )


# Association table for many-to-many relationship between campaigns and lead brand contacts
campaign_lead_contacts = sa.Table(
    "campaign_lead_contacts",
    BaseDBModel.metadata,
    sa.Column("campaign_id", sa.ForeignKey("campaigns.id"), primary_key=True),
    sa.Column("brand_contact_id", sa.ForeignKey("brand_contacts.id"), primary_key=True),
)


class CampaignGuest(BaseDBModel):
    """Campaign guest access model.

    Allows users to access specific campaigns without team membership.
    Used for magic link invitations and external collaborators.
    """

    __tablename__ = "campaign_guests"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id: Mapped[int] = mapped_column(
        sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    access_level: Mapped[CampaignGuestAccessLevel] = mapped_column(
        sa.Enum(CampaignGuestAccessLevel, native_enum=False, length=50),
        nullable=False,
        default=CampaignGuestAccessLevel.VIEWER,
    )
    invited_by_user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    campaign: Mapped["Campaign"] = relationship("Campaign")
    invited_by: Mapped["User | None"] = relationship(
        "User", foreign_keys=[invited_by_user_id]
    )

    # Unique constraint: a user can only have one access level per campaign
    __table_args__ = (
        sa.UniqueConstraint("user_id", "campaign_id", name="uq_user_campaign"),
    )


class PaymentBlock(RLSMixin(), BaseDBModel):
    """Payment block representing a milestone in campaign payment schedule.

    Payment blocks allow campaigns to have structured payment terms like:
    - 50% on contract signing
    - 25% on content delivery
    - 25% NET-30 after posting

    Each block can specify either a percentage or fixed amount, along with
    payment terms and what triggers the payment.
    """

    __tablename__ = "payment_blocks"

    # Foreign key to campaign
    campaign_id: Mapped[int] = mapped_column(
        sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Payment block details
    label: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    trigger: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)

    # Amount can be specified as either fixed USD or percentage
    amount_usd: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 2), nullable=True)
    percent: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(5, 2), nullable=True
    )  # 0.00 to 100.00

    # Payment terms in days (e.g., NET-30 = 30)
    net_days: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    # Order of payment blocks in the schedule
    order_index: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign", back_populates="payment_blocks"
    )

    # Constraints
    __table_args__ = (
        sa.CheckConstraint(
            "(percent IS NULL) OR (percent >= 0 AND percent <= 100)",
            name="ck_payment_percent_0_100",
        ),
        sa.Index("ix_payment_blocks_campaign_order", "campaign_id", "order_index"),
    )
