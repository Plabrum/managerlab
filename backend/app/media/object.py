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
            key="filename",
            label="Filename",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="image_link",
            label="Image Link",
            type=FieldType.URL,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.URL),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="thumnbnail_link",
            label="Thumbnail Link",
            type=FieldType.URL,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.URL),
            default_visible=False,
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
    def to_detail_dto(cls, media: Media) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="filename",
                value=media.filename,
                type=FieldType.String,
                label="Filename",
                editable=True,
            ),
            ObjectFieldDTO(
                key="image_link",
                value=media.image_link,
                type=FieldType.URL,
                label="Image Link",
                editable=True,
            ),
            ObjectFieldDTO(
                key="thumnbnail_link",
                value=media.thumnbnail_link,
                type=FieldType.URL,
                label="Thumbnail Link",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(media.id),
            object_type=ObjectTypes.Media,
            state="active",
            fields=fields,
            actions=[],
            created_at=media.created_at.isoformat(),
            updated_at=media.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, media: Media) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="filename",
                value=media.filename,
                type=FieldType.String,
                label="Filename",
                editable=False,
            ),
            ObjectFieldDTO(
                key="image_link",
                value=media.image_link,
                type=FieldType.URL,
                label="Image Link",
                editable=False,
            ),
            ObjectFieldDTO(
                key="thumnbnail_link",
                value=media.thumnbnail_link,
                type=FieldType.URL,
                label="Thumbnail Link",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(media.id),
            object_type=ObjectTypes.Media,
            title=media.filename,
            subtitle=media.image_link,
            state="active",
            actions=[],
            created_at=media.created_at.isoformat(),
            updated_at=media.updated_at.isoformat(),
            fields=fields,
        )
