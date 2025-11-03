from app.actions.enums import ActionGroupType
from app.documents.models import Document
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    DatetimeFieldValue,
    EnumFieldValue,
    FieldType,
    IntFieldValue,
    ObjectColumn,
    StringFieldValue,
)


class DocumentObject(BaseObject[Document]):
    object_type = ObjectTypes.Documents

    @classmethod
    def model(cls) -> type[Document]:
        return Document

    @classmethod
    def title_field(cls, document: Document) -> str:
        return document.file_name

    @classmethod
    def subtitle_field(cls, document: Document) -> str:
        return f"{document.file_type} - {document.mime_type}"

    @classmethod
    def state_field(cls, document: Document) -> str:
        return document.state

    # Action groups
    top_level_action_group = ActionGroupType.TopLevelDocumentActions
    action_group = ActionGroupType.DocumentActions

    column_definitions = [
        ObjectColumn(
            key="id",
            label="ID",
            type=FieldType.Int,
            value=lambda obj: IntFieldValue(value=obj.id),
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="file_name",
            label="File Name",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.file_name),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="file_type",
            label="Type",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.file_type),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="file_size",
            label="Size",
            type=FieldType.Int,
            value=lambda obj: IntFieldValue(value=obj.file_size),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="mime_type",
            label="MIME Type",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.mime_type),
            sortable=False,
            default_visible=False,
            editable=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="state",
            label="State",
            type=FieldType.Enum,
            value=lambda obj: EnumFieldValue(value=obj.state),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="created_at",
            label="Created",
            type=FieldType.Datetime,
            value=lambda obj: DatetimeFieldValue(value=obj.created_at),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            value=lambda obj: DatetimeFieldValue(value=obj.updated_at),
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
    ]
