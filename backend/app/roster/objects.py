from sqlalchemy.orm import joinedload

from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    EmailFieldValue,
    EnumFieldValue,
    FieldType,
    ObjectColumn,
    StringFieldValue,
    media_to_image_field_value,
)
from app.roster.enums import RosterStates
from app.roster.models import Roster


class RosterObject(BaseObject[Roster]):
    object_type = ObjectTypes.Roster

    @classmethod
    def model(cls) -> type[Roster]:
        return Roster

    @classmethod
    def title_field(cls, roster: Roster) -> str:
        return roster.name

    @classmethod
    def subtitle_field(cls, roster: Roster) -> str:
        return roster.instagram_handle or ""

    @classmethod
    def state_field(cls, roster: Roster) -> str:
        return roster.state

    # Action groups
    top_level_action_group = ActionGroupType.RosterActions

    # Load options
    load_options = [joinedload(Roster.user), joinedload(Roster.profile_photo)]

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
            key="email",
            label="Email",
            type=FieldType.Email,
            value=lambda obj: EmailFieldValue(value=obj.email) if obj.email else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="instagram_handle",
            label="Instagram",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.instagram_handle) if obj.instagram_handle else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="state",
            label="Status",
            type=FieldType.Enum,
            value=lambda obj: EnumFieldValue(value=obj.state),
            sortable=True,
            default_visible=True,
            available_values=[e.name for e in RosterStates],
            editable=False,
            include_in_list=True,
        ),
        ObjectColumn(
            key="profile_photo",
            label="Profile Photo",
            type=FieldType.Image,
            value=lambda obj: media_to_image_field_value(
                obj.profile_photo,
                BaseObject.registry.dependencies["s3_client"],
            )
            if obj.profile_photo
            else None,
            sortable=False,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="facebook_handle",
            label="Facebook",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.facebook_handle) if obj.facebook_handle else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="tiktok_handle",
            label="TikTok",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.tiktok_handle) if obj.tiktok_handle else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ObjectColumn(
            key="youtube_channel",
            label="YouTube",
            type=FieldType.String,
            value=lambda obj: StringFieldValue(value=obj.youtube_channel) if obj.youtube_channel else None,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
    ]
