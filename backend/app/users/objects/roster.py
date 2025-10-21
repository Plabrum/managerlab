from sqlalchemy.orm import joinedload

from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ActionDTO,
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    StringFieldValue,
    EmailFieldValue,
    EnumFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.users.enums import RosterStates
from app.users.models import Roster
from app.utils.sqids import sqid_encode


class RosterObject(BaseObject):
    object_type = ObjectTypes.Roster
    model = Roster

    @classmethod
    def get_top_level_action_group(cls):
        return ActionGroupType.TopLevelRosterActions

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
                value=StringFieldValue(value=roster_member.name),
                label="Name",
                editable=True,
            ),
            (
                ObjectFieldDTO(
                    key="email",
                    value=(EmailFieldValue(value=roster_member.email)),
                    label="Email",
                    editable=True,
                )
                if roster_member.email
                else None
            ),
            (
                ObjectFieldDTO(
                    key="phone",
                    value=(StringFieldValue(value=roster_member.phone)),
                    label="Phone",
                    editable=True,
                )
                if roster_member.phone
                else None
            ),
            (
                ObjectFieldDTO(
                    key="instagram_handle",
                    value=(StringFieldValue(value=roster_member.instagram_handle)),
                    label="Instagram Handle",
                    editable=True,
                )
                if roster_member.instagram_handle
                else None
            ),
            (
                ObjectFieldDTO(
                    key="owner",
                    value=(StringFieldValue(value=roster_member.user.name)),
                    label="Owner",
                    editable=False,
                )
                if roster_member.user
                else None
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(roster_member.id),
            object_type=ObjectTypes.Roster,
            state=roster_member.state.name,
            title=roster_member.name,
            fields=[f for f in fields if f is not None],
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
                value=StringFieldValue(value=roster_member.name),
                label="Name",
                editable=False,
            ),
            (
                ObjectFieldDTO(
                    key="email",
                    value=(EmailFieldValue(value=roster_member.email)),
                    label="Email",
                    editable=False,
                )
                if roster_member.email
                else None
            ),
            (
                ObjectFieldDTO(
                    key="instagram_handle",
                    value=(StringFieldValue(value=roster_member.instagram_handle)),
                    label="Instagram",
                    editable=False,
                )
                if roster_member.instagram_handle
                else None
            ),
            ObjectFieldDTO(
                key="state",
                value=EnumFieldValue(value=roster_member.state.name),
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
            fields=[f for f in fields if f is not None],
        )
