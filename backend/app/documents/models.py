"""Document model for file uploads."""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.base.models import BaseDBModel
from app.base.scope_mixins import RLSMixin
from app.base.threadable_mixin import ThreadableMixin
from app.documents.enums import DocumentStates
from app.state_machine.models import StateMachineMixin


class Document(
    ThreadableMixin,
    RLSMixin(scope_with_campaign_id=True),
    StateMachineMixin(state_enum=DocumentStates, initial_state=DocumentStates.PENDING),
    BaseDBModel,
):
    """Document model for file uploads (PDFs, Word docs, Excel, etc)."""

    __tablename__ = "documents"

    # File metadata
    file_key: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    file_type: Mapped[str] = mapped_column(sa.Text, nullable=False)  # e.g., 'pdf', 'docx', 'xlsx', 'txt'
    file_size: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # Optional: Preview/thumbnail for future enhancement
    thumbnail_key: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
