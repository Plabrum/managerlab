from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    FieldType,
    ObjectColumn,
    StringFieldValue,
)
from app.users.models import Team


class TeamObject(BaseObject[Team]):
    object_type = ObjectTypes.Teams

    @classmethod
    def model(cls) -> type[Team]:
        return Team

    @classmethod
    def title_field(cls, obj: Team) -> str:
        return obj.name

    @classmethod
    def subtitle_field(cls, obj: Team) -> str:
        return obj.description or ""

    column_definitions = [
        ObjectColumn(
            key="name",
            label="Name",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.name),
            sortable=True,
            default_visible=True,
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="description",
            label="Description",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.description) if obj.description else None,
            sortable=False,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
    ]
