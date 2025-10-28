from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.users.models import Team


class TeamObject(BaseObject):
    object_type = ObjectTypes.Teams
    model = Team

    # Title/subtitle configuration
    title_field = "name"
    subtitle_field = "description"

    column_definitions = [
        ColumnDefinitionDTO(
            key="name",
            label="Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="description",
            label="Description",
            type=FieldType.String,
            sortable=False,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
    ]
