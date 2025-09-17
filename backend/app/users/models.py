from sqlalchemy.orm import mapped_column
import sqlalchemy as sa

from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    email = mapped_column(sa.Text, unique=True, index=True, nullable=False)
    email_verified = mapped_column(sa.Boolean, default=False, nullable=False)
    created_at = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )
