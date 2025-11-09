from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseObjectAction, BaseTopLevelAction, action_group_factory
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse, DownloadFileActionResult
from app.client.s3_client import S3Client
from app.documents.enums import DocumentActions, DocumentStates
from app.documents.models import Document
from app.documents.schemas import DocumentUpdateSchema, RegisterDocumentSchema
from app.utils.db import update_model

# Create document action group
document_actions = action_group_factory(
    ActionGroupType.DocumentActions,
    model_type=Document,
)


@document_actions
class DeleteDocument(BaseObjectAction[Document]):
    action_key = DocumentActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this document?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(cls, obj: Document, data: Any, transaction: AsyncSession) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted document",
        )


@document_actions
class UpdateDocument(BaseObjectAction[Document]):
    action_key = DocumentActions.update
    label = "Update"
    is_bulk_allowed = True
    priority = 50
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Document,
        data: DocumentUpdateSchema,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=cls.deps.user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated document",
        )


@document_actions
class DownloadDocument(BaseObjectAction[Document]):
    action_key = DocumentActions.download
    label = "Download"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.download

    @classmethod
    async def execute(cls, obj: Document, data: Any, transaction: AsyncSession) -> ActionExecutionResponse:
        download_url = cls.deps.s3_client.generate_presigned_download_url(key=obj.file_key, expires_in=3600)

        return ActionExecutionResponse(
            message="Download ready",
            action_result=DownloadFileActionResult(
                url=download_url,
                filename=obj.file_name,
            ),
        )

    @classmethod
    def is_available(cls, obj: Document | None, **kwargs: Any) -> bool:
        return obj is not None and obj.state == DocumentStates.READY


@document_actions
class CreateDocument(BaseTopLevelAction):
    action_key = DocumentActions.register
    label = "Create Document"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: RegisterDocumentSchema,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        # Determine file type from mime_type or extension
        file_type = _determine_file_type(data.mime_type, data.file_name)

        document = Document(
            team_id=cls.deps.team_id,
            campaign_id=cls.deps.campaign_id,
            file_key=data.file_key,
            file_name=data.file_name,
            file_size=data.file_size,
            mime_type=data.mime_type,
            file_type=file_type,
            state=DocumentStates.READY,  # No processing needed initially
        )
        transaction.add(document)
        await transaction.flush()

        return ActionExecutionResponse(
            message=f"Created document '{document.file_name}'",
        )


def _determine_file_type(mime_type: str, file_name: str) -> str:
    """Determine document file type from MIME type or file extension."""
    mime_type_map = {
        "application/pdf": "pdf",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/plain": "txt",
        "text/markdown": "md",
        "text/csv": "csv",
    }

    if mime_type in mime_type_map:
        return mime_type_map[mime_type]

    if "." in file_name:
        extension = file_name.rsplit(".", 1)[-1].lower()
        return extension

    return "file"
