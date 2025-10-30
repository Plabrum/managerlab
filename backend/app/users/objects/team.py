from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    FieldType,
    ObjectColumn,
)
from app.users.models import Team


class TeamObject(BaseObject):
    object_type = ObjectTypes.Teams
    model = Team

    # Title/subtitle configuration
    title_field = "name"
    subtitle_field = "description"

    column_definitions = [
        ObjectColumn(
            key="name",
            label="Name",
            type=FieldType.String,
            value=lambda obj: obj.name,
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="description",
            label="Description",
            type=FieldType.String,
            value=lambda obj: obj.description,
            sortable=False,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
    ]
