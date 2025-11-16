"""OpenAI client wrapper for agent-based extraction tasks."""

import io
import logging
from abc import ABC, abstractmethod
from typing import Annotated, Any

from litestar.params import Dependency
from openai import AsyncOpenAI
from openai.types import FileObject
from openai.types.file_purpose import FilePurpose

from app.utils.configure import Config

logger = logging.getLogger(__name__)


class BaseOpenAIClient(ABC):
    """Abstract base class for OpenAI operations."""

    @abstractmethod
    async def upload_file(self, file_bytes: bytes, filename: str, purpose: FilePurpose = "assistants") -> FileObject:
        """
        Upload a file to OpenAI.

        Args:
            file_bytes: File contents as bytes
            filename: Original filename (used for content type detection)
            purpose: OpenAI file purpose (default: "assistants")

        Returns:
            FileObject with id, filename, bytes, created_at, etc.
        """
        pass

    @abstractmethod
    async def run_structured_extraction(
        self,
        file_id: str,
        instructions: str,
        schema_dict: dict[str, Any],
        model: str = "gpt-4o",
    ) -> dict[str, Any]:
        """
        Run structured extraction using OpenAI chat completion with file attachment.

        Args:
            file_id: OpenAI file ID from upload_file()
            instructions: System instructions for extraction
            schema_dict: JSON schema for structured output
            model: Model to use (default: gpt-4o)

        Returns:
            Parsed JSON object matching schema
        """
        pass

    @abstractmethod
    async def delete_file(self, file_id: str) -> None:
        """
        Delete a file from OpenAI storage.

        Args:
            file_id: OpenAI file ID to delete
        """
        pass


class OpenAIClient(BaseOpenAIClient):
    """Production OpenAI client implementation."""

    def __init__(self, api_key: str, organization: str | None = None, model: str = "gpt-4o"):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            organization: Optional organization ID
            model: Default model to use
        """
        self.client = AsyncOpenAI(api_key=api_key, organization=organization)
        self.default_model = model

    async def upload_file(self, file_bytes: bytes, filename: str, purpose: FilePurpose = "assistants") -> FileObject:
        """Upload file to OpenAI."""
        logger.info(f"Uploading file to OpenAI: {filename} ({len(file_bytes)} bytes)")

        # Create file-like object from bytes
        file_obj = io.BytesIO(file_bytes)
        file_obj.name = filename

        # Upload to OpenAI
        file_response = await self.client.files.create(file=file_obj, purpose=purpose)

        logger.info(f"File uploaded successfully: {file_response.id}")
        return file_response

    async def run_structured_extraction(
        self,
        file_id: str,
        instructions: str,
        schema_dict: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Run structured extraction with file attachment using OpenAI Responses API.

        Uses the responses.create() endpoint which supports:
        - File attachments with OCR for PDFs
        - Multi-modal parsing
        - Structured extraction with JSON schemas
        - Agent-style tool behaviors
        """
        model = model or self.default_model

        logger.info(f"Running structured extraction with model {model}, file_id={file_id}")

        try:
            import json

            # Use the Responses API which supports file attachments
            # Note: Type ignore needed due to dynamic API structure
            response = await self.client.responses.create(  # type: ignore
                model=model,
                instructions=instructions,
                attachments=[{"file_id": file_id}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "campaign_extraction",
                        "strict": True,
                        "schema": schema_dict,
                    },
                },
                temperature=0.1,  # Low temperature for consistent extraction
            )

            # Extract structured output from response
            # Response.output is a list of output items (messages, tool calls, etc.)
            # For structured outputs, we expect a message with JSON text
            if not response.output:
                raise ValueError("Empty output from OpenAI response")

            # Find the first message in the output
            for item in response.output:
                if item.type == "message" and hasattr(item, "content"):
                    # item.content is a list of content blocks (text, refusal, etc.)
                    for content_block in item.content:
                        if content_block.type == "output_text":
                            # Parse the JSON from the text
                            result = json.loads(content_block.text)
                            logger.info("Structured extraction completed successfully")
                            return result

            raise ValueError(f"No text content found in OpenAI response output: {response.output}")

        except Exception as e:
            logger.error(f"Structured extraction failed: {e}")
            raise

    async def delete_file(self, file_id: str) -> None:
        """Delete file from OpenAI storage."""
        logger.info(f"Deleting file from OpenAI: {file_id}")
        try:
            await self.client.files.delete(file_id)
            logger.info(f"File deleted successfully: {file_id}")
        except Exception as e:
            logger.warning(f"Failed to delete file {file_id}: {e}")
            # Don't raise - file cleanup is best-effort


class LocalOpenAIClient(BaseOpenAIClient):
    """Mock OpenAI client for development/testing."""

    async def upload_file(self, file_bytes: bytes, filename: str, purpose: FilePurpose = "assistants") -> FileObject:
        """Mock file upload - returns dummy FileObject."""
        logger.info(f"[LOCAL] Mock upload: {filename} ({len(file_bytes)} bytes)")

        # Create mock FileObject
        # Note: This is a simplified mock - adjust fields as needed
        return FileObject(
            id=f"file-mock-{hash(filename) % 10000}",
            bytes=len(file_bytes),
            created_at=1234567890,
            filename=filename,
            object="file",
            purpose="assistants",  # Use literal for mock
            status="processed",
        )

    async def run_structured_extraction(
        self,
        file_id: str,
        instructions: str,
        schema_dict: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        """Mock extraction - returns dummy structured data."""
        logger.info(f"[LOCAL] Mock extraction for file_id={file_id}")

        # Return dummy campaign data matching schema
        return {
            "name": "Mock Campaign from Local Client",
            "description": "This is a mock campaign created by LocalOpenAIClient for testing",
            "counterparty_type": "BRAND",
            "counterparty_name": "Acme Corp",
            "counterparty_email": "contracts@acme.com",
            "compensation_structure": "FLAT_FEE",
            "compensation_total_usd": 5000.0,
            "payment_terms_days": 30,
            "payment_blocks": [
                {"label": "Upfront", "trigger": "Upon signing", "amount_usd": 2500.0, "net_days": 0},
                {"label": "Final", "trigger": "Upon delivery", "amount_usd": 2500.0, "net_days": 30},
            ],
            "flight_start_date": "2025-02-01",
            "flight_end_date": "2025-03-01",
            "ftc_string": "#ad #sponsored",
            "usage_duration": 365,
            "usage_territory": "Worldwide",
            "usage_paid_media_option": True,
            "exclusivity_category": "Beauty",
            "exclusivity_days_before": 30,
            "exclusivity_days_after": 60,
            "ownership_mode": "BRAND_OWNED",
            "approval_rounds": 2,
            "approval_sla_hours": 48,
            "confidence_score": 0.95,
            "extraction_notes": "Mock extraction - all fields are dummy data",
        }

    async def delete_file(self, file_id: str) -> None:
        """Mock file deletion."""
        logger.info(f"[LOCAL] Mock delete: {file_id}")


def provide_openai_client(config: Config) -> BaseOpenAIClient:
    """
    Factory function to provide appropriate OpenAI client based on environment.

    Args:
        config: Application configuration

    Returns:
        BaseOpenAIClient implementation (real or mock)
    """
    if config.IS_DEV and not config.OPENAI_API_KEY:
        logger.info("Using LocalOpenAIClient (no API key in development)")
        return LocalOpenAIClient()

    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required in production")

    logger.info("Using OpenAI production client")
    return OpenAIClient(
        api_key=config.OPENAI_API_KEY,
        organization=config.OPENAI_ORG_ID,
        model=config.OPENAI_MODEL,
    )


# Litestar dependency injection
OpenAIClientDep = Annotated[BaseOpenAIClient, Dependency(skip_validation=True)]
