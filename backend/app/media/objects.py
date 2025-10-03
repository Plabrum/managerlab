from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.media.models import Media
from app.utils.sqids import sqid_encode


class MediaObject(BaseObject):
    object_type = ObjectTypes.Media
    model = Media
    column_definitions = [
        ColumnDefinitionDTO(
            key="file_name",
            label="File Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
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
            key="status",
            label="Status",
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
    def to_detail_dto(
        cls, object: Media, context: dict | None = None
    ) -> ObjectDetailDTO:
        media = object
        # Extract s3_client from context if provided
        s3_client = context.get("s3_client") if context else None

        # Generate presigned URLs if s3_client is available
        view_url = (
            s3_client.generate_presigned_download_url(
                key=media.file_key, expires_in=3600
            )
            if s3_client
            else None
        )
        thumbnail_url = (
            s3_client.generate_presigned_download_url(
                key=media.thumbnail_key, expires_in=3600
            )
            if s3_client and media.thumbnail_key
            else None
        )

        fields = [
            ObjectFieldDTO(
                key="file_name",
                value=media.file_name,
                type=FieldType.String,
                label="File Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="file_type",
                value=media.file_type,
                type=FieldType.String,
                label="File Type",
                editable=False,
            ),
            ObjectFieldDTO(
                key="file_size",
                value=media.file_size,
                type=FieldType.Int,
                label="File Size",
                editable=False,
            ),
            ObjectFieldDTO(
                key="mime_type",
                value=media.mime_type,
                type=FieldType.String,
                label="MIME Type",
                editable=False,
            ),
            ObjectFieldDTO(
                key="status",
                value=media.status,
                type=FieldType.String,
                label="Status",
                editable=False,
            ),
            ObjectFieldDTO(
                key="view_url",
                value=view_url,
                type=FieldType.URL,
                label="View URL",
                editable=False,
            ),
            ObjectFieldDTO(
                key="thumbnail_url",
                value=thumbnail_url or view_url,
                type=FieldType.URL,
                label="Thumbnail URL",
                editable=False,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(media.id),
            object_type=ObjectTypes.Media,
            state=media.status,
            title=media.file_name,
            fields=fields,
            actions=[],
            created_at=media.created_at,
            updated_at=media.updated_at,
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, object: Media, context: dict | None = None) -> ObjectListDTO:
        media = object
        # Extract s3_client from context if provided
        s3_client = context.get("s3_client") if context else None

        # Generate presigned URLs if s3_client is available
        view_url = (
            s3_client.generate_presigned_download_url(
                key=media.file_key, expires_in=3600
            )
            if s3_client
            else None
        )
        thumbnail_url = (
            s3_client.generate_presigned_download_url(
                key=media.thumbnail_key, expires_in=3600
            )
            if s3_client and media.thumbnail_key
            else None
        )

        fields = [
            ObjectFieldDTO(
                key="file_name",
                value=media.file_name,
                type=FieldType.String,
                label="File Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="file_type",
                value=media.file_type,
                type=FieldType.String,
                label="Type",
                editable=False,
            ),
            ObjectFieldDTO(
                key="file_size",
                value=media.file_size,
                type=FieldType.Int,
                label="Size",
                editable=False,
            ),
            ObjectFieldDTO(
                key="status",
                value=media.status,
                type=FieldType.String,
                label="Status",
                editable=False,
            ),
            ObjectFieldDTO(
                key="view_url",
                value=view_url,
                type=FieldType.URL,
                label="View URL",
                editable=False,
            ),
            ObjectFieldDTO(
                key="thumbnail_url",
                value=thumbnail_url or view_url,
                type=FieldType.URL,
                label="Thumbnail",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(media.id),
            object_type=ObjectTypes.Media,
            title=media.file_name,
            subtitle=f"{media.file_type} - {media.mime_type}",
            state=media.status,
            actions=[],
            created_at=media.created_at,
            updated_at=media.updated_at,
            fields=fields,
        )
