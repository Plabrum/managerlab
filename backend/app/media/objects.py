from app.actions.enums import ActionGroupType
from app.media.models import Media
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    DatetimeFieldValue,
    EnumFieldValue,
    FieldType,
    IntFieldValue,
    ObjectColumn,
    StringFieldValue,
    media_to_image_field_value,
)


class MediaObject(BaseObject[Media]):
    object_type = ObjectTypes.Media

    @classmethod
    def model(cls) -> type[Media]:
        return Media

    @classmethod
    def title_field(cls, media: Media) -> str:
        return media.file_name

    @classmethod
    def subtitle_field(cls, media: Media) -> str:
        return f"{media.file_type} - {media.mime_type}"

    @classmethod
    def state_field(cls, media: Media) -> str:
        return media.state

    # Action groups
    top_level_action_group = ActionGroupType.TopLevelMediaActions
    action_group = ActionGroupType.MediaActions

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
            key="file_info",
            label="File Info",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=f"{obj.file_type} - {obj.mime_type}"),
            sortable=False,
            default_visible=False,
            editable=False,
            include_in_list=False,
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
            key="image",
            label="Image",
            type=FieldType.Image,
            value=lambda obj: media_to_image_field_value(obj, BaseObject.registry.dependencies["s3_client"]),
            sortable=False,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
    ]
