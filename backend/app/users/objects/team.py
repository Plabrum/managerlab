from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ActionDTO,
    ObjectListDTO,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    StringFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.users.models import Team
from app.utils.sqids import sqid_encode


class TeamObject(BaseObject):
    object_type = ObjectTypes.Teams
    model = Team
    column_definitions = [
        ColumnDefinitionDTO(
            key="name",
            label="Name",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="description",
            label="Description",
            type=FieldType.Text,
            sortable=False,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
    ]

    @classmethod
    async def to_list_dto(cls, team: Team) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=StringFieldValue(value=team.name),
                label="Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="description",
                value=StringFieldValue(value=team.description or ""),
                label="Description",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(team.id),
            object_type=ObjectTypes.Teams,
            title=team.name,
            subtitle=team.description,
            state="active",  # Teams don't have a state machine, so we use a default value
            actions=[
                ActionDTO(action="delete", label="Delete", is_bulk_allowed=False),
            ],
            created_at=team.created_at,
            updated_at=team.updated_at,
            fields=fields,
        )
