from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseAction, action_group_factory
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse, DownloadFileActionResult
from app.client.s3_client import S3Client
from app.documents.enums import DocumentActions, DocumentStates
from app.documents.models import Document
from app.documents.schemas import DocumentUpdateSchema
from app.utils.db import update_model

# Create document action group
document_actions = action_group_factory(
    ActionGroupType.DocumentActions,
    model_type=Document,
)


@document_actions
class DeleteDocument(BaseAction):
    action_key = DocumentActions.delete
    label = "Delete"
    is_bulk_allowed = True
    priority = 0
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this document?"
    should_redirect_to_parent = True

    @classmethod
    async def execute(
        cls,
        obj: Document,
        transaction: AsyncSession,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(
            message="Deleted document",
        )


@document_actions
class UpdateDocument(BaseAction):
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
        user: int,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Updated document",
        )


@document_actions
class DownloadDocument(BaseAction):
    action_key = DocumentActions.download
    label = "Download"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.download

    @classmethod
    async def execute(
        cls,
        obj: Document,
        s3_client: S3Client,
    ) -> ActionExecutionResponse:
        download_url = s3_client.generate_presigned_download_url(key=obj.file_key, expires_in=3600)

        return ActionExecutionResponse(
            message="Download ready",
            action_result=DownloadFileActionResult(
                url=download_url,
                filename=obj.file_name,
            ),
        )

    @classmethod
    def is_available(cls, obj: Document | None) -> bool:
        return obj is not None and obj.state == DocumentStates.READY
