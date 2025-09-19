from sqlalchemy.orm import mapped_column
import sqlalchemy as sa

from app.models.base import BaseDBModel


class User(BaseDBModel):
    __tablename__ = "users"
    name = mapped_column(sa.Text, index=True, nullable=False)
    email = mapped_column(sa.Text, unique=True, index=True, nullable=False)
    email_verified = mapped_column(sa.Boolean, default=False, nullable=False)


class WaitlistEntry(BaseDBModel):
    __tablename__ = "waitlist_entries"
    name = mapped_column(sa.Text, index=True, nullable=False)
    email = mapped_column(sa.Text, index=True, nullable=False)
    company = mapped_column(sa.Text, nullable=True)
    message = mapped_column(sa.Text, nullable=True)
