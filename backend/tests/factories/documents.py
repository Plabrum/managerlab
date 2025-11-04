"""Factory for Document model."""

from app.documents.enums import DocumentStates
from app.documents.models import Document
from tests.factories.base import BaseFactory


class DocumentFactory(BaseFactory[Document]):
    """Factory for Document model."""

    __model__ = Document
    __set_relationships__ = False

    @classmethod
    def file_key(cls) -> str:
        """Generate a unique file key."""
        import uuid

        return f"documents/{uuid.uuid4()}/test-document.pdf"

    @classmethod
    def file_name(cls) -> str:
        """Generate a file name."""
        return "test-document.pdf"

    @classmethod
    def file_type(cls) -> str:
        """Generate a file type."""
        return "pdf"

    @classmethod
    def mime_type(cls) -> str:
        """Generate a MIME type."""
        return "application/pdf"

    @classmethod
    def file_size(cls) -> int:
        """Generate a file size in bytes."""
        return 1024 * 100  # 100KB

    @classmethod
    def state(cls) -> DocumentStates:
        """Generate a document state."""
        return DocumentStates.READY

    campaign_id = None  # Must be explicitly provided if needed
    deleted_at = None  # Ensure documents are not soft-deleted by default
