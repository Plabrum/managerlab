from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.campaigns.enums import CampaignStates, CampaignGuestAccessLevel
from app.state_machine.models import StateMachineMixin

if TYPE_CHECKING:
    from app.deliverables.models import Deliverable
    from app.brands.models.brands import Brand
    from app.brands.models.contacts import BrandContact
    from app.payments.models import Invoice
    from app.users.models import User


class Campaign(
    RLSMixin(),
    StateMachineMixin(
        state_enum=CampaignStates,
        initial_state=CampaignStates.DRAFT,
    ),
    BaseDBModel,
):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Foreign keys - Campaign always has a Brand
    brand_id: Mapped[int] = mapped_column(sa.ForeignKey("brands.id"), nullable=False)

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="campaigns")
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
