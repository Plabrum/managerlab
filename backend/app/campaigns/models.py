from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseDBModel

if TYPE_CHECKING:
    from app.posts.models import Post
    from app.brands.models.brands import Brand
    from app.brands.models.contacts import BrandContact
    from app.payments.models import Invoice


class Campaign(BaseDBModel):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Foreign keys - Campaign always has a Brand
    brand_id: Mapped[int] = mapped_column(sa.ForeignKey("brands.id"), nullable=False)

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="campaigns")
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="campaign")
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
