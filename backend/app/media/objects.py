from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
from app.client.s3_client import S3Client
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    DatetimeFieldValue,
    EnumFieldValue,
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    StringFieldValue,
    IntFieldValue,
    ImageFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.media.models import Media
from app.utils.sqids import sqid_encode


class MediaObject(BaseObject):
    object_type = ObjectTypes.Media
    model = Media

    @classmethod
    def get_top_level_action_group(cls):
        return ActionGroupType.TopLevelMediaActions

    column_definitions = [
        ColumnDefinitionDTO(
            key="id",
            label="ID",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=False,
        ),
        ColumnDefinitionDTO(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
        ),
        ColumnDefinitionDTO(
            key="file_name",
            label="File Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="image",
            label="Image",
            type=FieldType.Image,
            sortable=False,
            filter_type=get_filter_by_field_type(FieldType.Image),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="file_type",
            label="Type",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="file_size",
            label="Size",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="state",
            label="State",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=True,
        ),
    ]

    @classmethod
    def to_detail_dto(cls, object: Media) -> ObjectDetailDTO:
        s3_client: S3Client = cls.registry.dependencies["s3_client"]
        view_url = s3_client.generate_presigned_download_url(
            key=object.file_key, expires_in=3600
        )
        thumbnail_url = (
            s3_client.generate_presigned_download_url(
                key=object.thumbnail_key, expires_in=3600
            )
            if object.thumbnail_key
            else None
        )

        fields = [
            ObjectFieldDTO(
                key="file_name",
                value=StringFieldValue(value=object.file_name),
                label="File Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="file_type",
                value=StringFieldValue(value=object.file_type),
                label="File Type",
                editable=False,
            ),
            ObjectFieldDTO(
                key="file_size",
                value=IntFieldValue(value=object.file_size),
                label="File Size",
                editable=False,
            ),
            ObjectFieldDTO(
                key="mime_type",
                value=StringFieldValue(value=object.mime_type),
                label="MIME Type",
                editable=False,
            ),
            ObjectFieldDTO(
                key="state",
                value=EnumFieldValue(value=object.state.value),
                label="State",
                editable=False,
            ),
            ObjectFieldDTO(
                key="created_at",
                value=DatetimeFieldValue(value=object.created_at),
                label="Created At",
                editable=False,
            ),
            ObjectFieldDTO(
                key="image",
                value=ImageFieldValue(
                    url=view_url,
                    thumbnail_url=thumbnail_url,
                ),
                label="Image",
                editable=False,
            ),
        ]

        action_class = ActionRegistry().get_class(ActionGroupType.MediaActions)
        actions = action_class.get_available_actions(obj=object)

        return ObjectDetailDTO(
            id=sqid_encode(object.id),
            object_type=ObjectTypes.Media,
            state=object.state,
            title=object.file_name,
            fields=fields,
            actions=actions,
            created_at=object.created_at,
            updated_at=object.updated_at,
        )

    @classmethod
    def to_list_dto(cls, object: Media) -> ObjectListDTO:
        s3_client: S3Client = cls.registry.dependencies["s3_client"]
        view_url = s3_client.generate_presigned_download_url(
            key=object.file_key, expires_in=3600
        )
        thumbnail_url = (
            s3_client.generate_presigned_download_url(
                key=object.thumbnail_key, expires_in=3600
            )
            if object.thumbnail_key
            else None
        )

        fields = [
            ObjectFieldDTO(
                key="file_name",
                value=StringFieldValue(value=object.file_name),
                label="File Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="file_type",
                value=StringFieldValue(value=object.file_type),
                label="Type",
                editable=False,
            ),
            ObjectFieldDTO(
                key="file_size",
                value=IntFieldValue(value=object.file_size),
                label="Size",
                editable=False,
            ),
            ObjectFieldDTO(
                key="state",
                value=EnumFieldValue(value=object.state.value),
                label="State",
                editable=False,
            ),
            ObjectFieldDTO(
                key="created_at",
                value=DatetimeFieldValue(value=object.created_at),
                label="Created At",
                editable=False,
            ),
            ObjectFieldDTO(
                key="image",
                value=ImageFieldValue(
                    url=view_url,
                    thumbnail_url=thumbnail_url,
                ),
                label="Image",
                editable=False,
            ),
        ]

        action_group = ActionRegistry().get_class(ActionGroupType.MediaActions)
        actions = action_group.get_available_actions(obj=object)

        return ObjectListDTO(
            id=sqid_encode(object.id),
            object_type=ObjectTypes.Media,
            title=object.file_name,
            subtitle=f"{object.file_type} - {object.mime_type}",
            state=object.state,
            actions=actions,
            created_at=object.created_at,
            updated_at=object.updated_at,
            fields=fields,
        )
