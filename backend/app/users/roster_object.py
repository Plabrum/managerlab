from sqlalchemy.orm import joinedload

from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ActionDTO,
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
)
from app.objects.services import get_filter_by_field_type
from app.users.enums import RosterStates
from app.users.models import Roster
from app.utils.sqids import sqid_encode


class RosterObject(BaseObject):
    object_type = ObjectTypes.Roster
    model = Roster
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
            key="email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="instagram_handle",
            label="Instagram",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
        ),
        ColumnDefinitionDTO(
            key="state",
            label="Status",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            available_values=[e.name for e in RosterStates],
        ),
    ]

    @classmethod
    def get_load_options(cls):
        """Return load options for eager loading relationships."""
        return [joinedload(Roster.user)]

    @classmethod
    def to_detail_dto(cls, roster_member: Roster) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=roster_member.name,
                type=FieldType.String,
                label="Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="email",
                value=roster_member.email,
                type=FieldType.Email,
                label="Email",
                editable=True,
            ),
            ObjectFieldDTO(
                key="phone",
                value=roster_member.phone,
                type=FieldType.String,
                label="Phone",
                editable=True,
            ),
            ObjectFieldDTO(
                key="instagram_handle",
                value=roster_member.instagram_handle,
                type=FieldType.String,
                label="Instagram Handle",
                editable=True,
            ),
            ObjectFieldDTO(
                key="owner",
                value=roster_member.user.name if roster_member.user else None,
                type=FieldType.String,
                label="Owner",
                editable=False,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(roster_member.id),
            object_type=ObjectTypes.Roster,
            state=roster_member.state.name,
            title=roster_member.name,
            fields=fields,
            actions=[
                ActionDTO(action="edit", label="Edit"),
                ActionDTO(action="archive", label="Archive"),
            ],
            created_at=roster_member.created_at,
            updated_at=roster_member.updated_at,
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, roster_member: Roster) -> ObjectListDTO:
        fields = [
            ObjectFieldDTO(
                key="name",
                value=roster_member.name,
                type=FieldType.String,
                label="Name",
                editable=False,
            ),
            ObjectFieldDTO(
                key="email",
                value=roster_member.email,
                type=FieldType.Email,
                label="Email",
                editable=False,
            ),
            ObjectFieldDTO(
                key="instagram_handle",
                value=roster_member.instagram_handle,
                type=FieldType.String,
                label="Instagram",
                editable=False,
            ),
            ObjectFieldDTO(
                key="state",
                value=roster_member.state.name,
                type=FieldType.Enum,
                label="Status",
                editable=False,
            ),
        ]

        return ObjectListDTO(
            id=sqid_encode(roster_member.id),
            object_type=ObjectTypes.Roster,
            title=roster_member.name,
            subtitle=roster_member.instagram_handle,
            state=roster_member.state.name,
            actions=[
                ActionDTO(action="edit", label="Edit", is_bulk_allowed=False),
                ActionDTO(action="archive", label="Archive", is_bulk_allowed=True),
            ],
            created_at=roster_member.created_at,
            updated_at=roster_member.updated_at,
            fields=fields,
        )
