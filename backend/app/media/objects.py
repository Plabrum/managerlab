from app.actions.enums import ActionGroupType
from app.client.s3_client import S3Client
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    FieldType,
    ObjectColumn,
)
from app.media.models import Media


class MediaObject(BaseObject):
    object_type = ObjectTypes.Media
    model = Media

    # Title/subtitle configuration
    title_field = "file_name"
    subtitle_field = "file_info"
    state_field = "state"

    # Action groups
    top_level_action_group = ActionGroupType.TopLevelMediaActions
    action_group = ActionGroupType.MediaActions

    @staticmethod
    def _format_image_urls(obj: Media):
        """Generate S3 presigned URLs for image."""
        s3_client: S3Client = MediaObject.registry.dependencies["s3_client"]
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
        return {"url": view_url, "thumbnail_url": thumbnail_url}

    column_definitions = [
        ObjectColumn(
            key="id",
            label="ID",
            type=FieldType.Int,
            value=lambda obj: obj.id,
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="file_info",
            label="File Info",
            type=FieldType.String,
            value=lambda obj: f"{obj.file_type} - {obj.mime_type}",
            sortable=False,
            default_visible=False,
            editable=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="updated_at",
            label="Updated At",
            type=FieldType.Datetime,
            value=lambda obj: obj.updated_at,
            sortable=True,
            default_visible=False,
            include_in_list=False,
        ),
        ObjectColumn(
            key="file_name",
            label="File Name",
            type=FieldType.String,
            value=lambda obj: obj.file_name,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="file_type",
            label="Type",
            type=FieldType.String,
            value=lambda obj: obj.file_type,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="file_size",
            label="Size",
            type=FieldType.Int,
            value=lambda obj: obj.file_size,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="state",
            label="State",
            type=FieldType.Enum,
            value=lambda obj: obj.state,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="created_at",
            label="Created",
            type=FieldType.Datetime,
            value=lambda obj: obj.created_at,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="image",
            label="Image",
            type=FieldType.Image,
            value=lambda obj: MediaObject._format_image_urls(obj),
            sortable=False,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
    ]
