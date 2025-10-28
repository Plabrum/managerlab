from typing import List

from app.actions.enums import ActionGroupType
from app.client.s3_client import S3Client
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    ImageFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.media.models import Media


class MediaObject(BaseObject):
    object_type = ObjectTypes.Media
    model = Media

    # Title/subtitle configuration
    title_field = "file_name"
    state_field = "state"

    # Action groups
    top_level_action_group = ActionGroupType.TopLevelMediaActions
    action_group = ActionGroupType.MediaActions

    @classmethod
    def to_list_dto(cls, obj: Media):
        dto = super().to_list_dto(obj)
        # Custom subtitle with file type and mime type
        dto.subtitle = f"{obj.file_type} - {obj.mime_type}"
        return dto

    @classmethod
    def get_custom_fields(cls, obj: Media) -> List[ObjectFieldDTO]:
        """Add custom image field with S3 presigned URLs."""
        s3_client: S3Client = cls.registry.dependencies["s3_client"]
        view_url = s3_client.generate_presigned_download_url(
            key=obj.file_key, expires_in=3600
        )
        thumbnail_url = (
            s3_client.generate_presigned_download_url(
                key=obj.thumbnail_key, expires_in=3600
            )
            if obj.thumbnail_key
            else None
        )

        return [
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

    column_definitions = [
        ColumnDefinitionDTO(
            key="id",
            label="ID",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=False,
            include_in_list=False,
        ),
        ColumnDefinitionDTO(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=False,
            include_in_list=False,
        ),
        ColumnDefinitionDTO(
            key="file_name",
            label="File Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="file_type",
            label="Type",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="file_size",
            label="Size",
            type=FieldType.Int,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Int),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="state",
            label="State",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="created_at",
            label="Created",
            type=FieldType.Datetime,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Datetime),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        # Image is handled via get_custom_fields() with S3 URL generation
    ]
