"""OpenAI client wrapper for agent-based extraction tasks."""

import io
import logging
from contextlib import asynccontextmanager
from typing import Annotated, AsyncIterator

import msgspec
from litestar.params import Dependency
from openai import AsyncOpenAI
from openai.types import FileObject
from openai.types.file_purpose import FilePurpose

from app.client.s3_client import BaseS3Client
from app.utils.configure import ConfigProtocol

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI client for file upload and structured extraction."""

    def __init__(
        self,
        api_key: str,
        s3_client: BaseS3Client,
        organization: str | None = None,
        model: str = "gpt-4o",
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            s3_client: S3 client for downloading files
            organization: Optional organization ID
            model: Default model to use
        """
        self.client = AsyncOpenAI(api_key=api_key, organization=organization)
        self.s3_client = s3_client
        self.default_model = model

    async def upload_file_from_s3(self, s3_key: str, purpose: FilePurpose = "assistants") -> FileObject:
        """
        Upload a file from S3 to OpenAI.

        Args:
            s3_key: S3 key of the file to upload
            purpose: OpenAI file purpose (default: "assistants")

        Returns:
            FileObject with id, filename, bytes, created_at, etc.
        """
        # Download file from S3
        file_bytes = self.s3_client.get_file_bytes(s3_key)

        # Extract filename from S3 key (take last part of path)
        filename = s3_key.split("/")[-1]

        logger.info(f"Uploading file to OpenAI: {filename} ({len(file_bytes)} bytes)")

        # Create file-like object from bytes
        file_obj = io.BytesIO(file_bytes)
        file_obj.name = filename

        # Upload to OpenAI
        file_response = await self.client.files.create(file=file_obj, purpose=purpose)

        logger.info(f"File uploaded successfully: {file_response.id}")
        return file_response

    @asynccontextmanager
    async def with_uploaded_file(self, s3_key: str, purpose: FilePurpose = "assistants") -> AsyncIterator[str]:
        """
        Context manager that uploads a file and ensures cleanup.

        Usage:
            async with openai_client.with_uploaded_file(s3_key) as file_id:
                result = await openai_client.run_structured_extraction(file_id, ...)

        Args:
            s3_key: S3 key of the file to upload
            purpose: OpenAI file purpose (default: "assistants")

        Yields:
            file_id: OpenAI file ID
        """
        file_obj = await self.upload_file_from_s3(s3_key, purpose=purpose)
        file_id = file_obj.id

        try:
            yield file_id
        finally:
            # Always clean up the file
            await self.delete_file(file_id)

    async def run_structured_extraction[T: msgspec.Struct](
        self,
        file_id: str,
        instructions: str,
        schema_type: type[T],
        model: str | None = None,
    ) -> T:
        """
        Run structured extraction with file attachment using OpenAI Responses API.

        Uses the responses.create() endpoint which supports:
        - File attachments with OCR for PDFs
        - Multi-modal parsing
        - Structured extraction with JSON schemas
        - Agent-style tool behaviors

        Args:
            file_id: OpenAI file ID from upload_file()
            instructions: User message/instructions for extraction
            schema_type: msgspec.Struct type for structured output
            model: Model to use (default: uses client's default_model)

        Returns:
            Typed instance of schema_type with extracted data
        """
        model = model or self.default_model

        logger.info(f"Running structured extraction with model {model}, file_id={file_id}")

        try:
            # Generate JSON schema from msgspec type
            schema_dict = msgspec.json.schema(schema_type)

            # Extract actual schema if it uses $ref (msgspec wraps schemas in $ref/$defs)
            if "$ref" in schema_dict and "$defs" in schema_dict:
                ref_name = schema_dict["$ref"].split("/")[-1]
                actual_schema = schema_dict["$defs"][ref_name]
            else:
                actual_schema = schema_dict

            # OpenAI strict mode requires:
            # 1. additionalProperties: false
            # 2. All properties must be in required array
            actual_schema["additionalProperties"] = False
            if "properties" in actual_schema:
                actual_schema["required"] = list(actual_schema["properties"].keys())

            # Use the Responses API with correct input format for file attachments
            # Files must be specified in the input array with type "input_file"
            # Structured output uses "text.format" not "response_format"
            # Note: Type ignore needed due to dynamic API structure
            response = await self.client.responses.create(  # type: ignore
                model=model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_file",
                                "file_id": file_id,
                            },
                            {
                                "type": "input_text",
                                "text": instructions,
                            },
                        ],
                    },
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_type.__name__,
                        "strict": True,
                        "schema": actual_schema,
                    }
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
                            # Parse JSON and validate with msgspec
                            json_bytes = content_block.text.encode("utf-8")
                            result = msgspec.json.decode(json_bytes, type=schema_type)
                            logger.info(f"Structured extraction completed successfully: {type(result).__name__}")
                            return result

            raise ValueError(f"No text content found in OpenAI response output: {response.output}")

        except Exception as e:
            logger.error(f"Structured extraction failed: {e}")
            raise

    async def delete_file(self, file_id: str) -> None:
        """
        Delete a file from OpenAI storage.

        Args:
            file_id: OpenAI file ID to delete
        """
        logger.info(f"Deleting file from OpenAI: {file_id}")
        try:
            await self.client.files.delete(file_id)
            logger.info(f"File deleted successfully: {file_id}")
        except Exception as e:
            logger.warning(f"Failed to delete file {file_id}: {e}")
            # Don't raise - file cleanup is best-effort


def provide_openai_client(config: ConfigProtocol, s3_client: BaseS3Client) -> OpenAIClient:
    logger.info("Initializing OpenAI client")
    return OpenAIClient(
        api_key=config.OPENAI_API_KEY,
        s3_client=s3_client,
        organization=config.OPENAI_ORG_ID,
        model=config.OPENAI_MODEL,
    )


# Litestar dependency injection
OpenAIClientDep = Annotated[OpenAIClient, Dependency(skip_validation=True)]
