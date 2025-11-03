from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import ActionGroupType, BaseAction, action_group_factory
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.documents.enums import DocumentStates, TopLevelDocumentActions
from app.documents.models import Document
from app.documents.schemas import RegisterDocumentSchema

top_level_document_actions = action_group_factory(ActionGroupType.TopLevelDocumentActions)


@top_level_document_actions
class CreateDocument(BaseAction):
    action_key = TopLevelDocumentActions.create
    label = "Create Document"
    is_bulk_allowed = False
    priority = 1
    icon = ActionIcon.add

    @classmethod
    async def execute(
        cls,
        data: RegisterDocumentSchema,
        transaction: AsyncSession,
        team_id: int | None = None,
        campaign_id: int | None = None,
    ) -> ActionExecutionResponse:
        # Determine file type from mime_type or extension
        file_type = _determine_file_type(data.mime_type, data.file_name)

        document = Document(
            team_id=team_id,
            campaign_id=campaign_id,
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
