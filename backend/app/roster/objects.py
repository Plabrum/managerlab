from sqlalchemy.orm import joinedload

from app.actions.enums import ActionGroupType
from app.actions.registry import ActionRegistry
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
    ImageFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.roster.enums import RosterStates
from app.roster.models import Roster
from app.utils.sqids import sqid_encode
from app.client.s3_client import S3Client


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
        return [joinedload(Roster.user), joinedload(Roster.profile_photo)]

    @classmethod
    def to_detail_dto(cls, roster_member: Roster) -> ObjectDetailDTO:
        # Generate profile photo URLs if available
        profile_photo_field = None
        if roster_member.profile_photo:
            s3_client: S3Client = cls.registry.dependencies["s3_client"]
            photo_url = s3_client.generate_presigned_download_url(
                key=roster_member.profile_photo.file_key, expires_in=3600
            )
            thumbnail_url = (
                s3_client.generate_presigned_download_url(
                    key=roster_member.profile_photo.thumbnail_key, expires_in=3600
                )
                if roster_member.profile_photo.thumbnail_key
                else None
            )
            profile_photo_field = ObjectFieldDTO(
                key="profile_photo",
                value=ImageFieldValue(url=photo_url, thumbnail_url=thumbnail_url),
                label="Profile Photo",
                editable=True,
            )

        fields = [
            profile_photo_field,
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
                    key="facebook_handle",
                    value=(StringFieldValue(value=roster_member.facebook_handle)),
                    label="Facebook Handle",
                    editable=True,
                )
                if roster_member.facebook_handle
                else None
            ),
            (
                ObjectFieldDTO(
                    key="tiktok_handle",
                    value=(StringFieldValue(value=roster_member.tiktok_handle)),
                    label="TikTok Handle",
                    editable=True,
                )
                if roster_member.tiktok_handle
                else None
            ),
            (
                ObjectFieldDTO(
                    key="youtube_channel",
                    value=(StringFieldValue(value=roster_member.youtube_channel)),
                    label="YouTube Channel",
                    editable=True,
                )
                if roster_member.youtube_channel
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

        # Get available actions for this roster member
        action_group = ActionRegistry().get_class(ActionGroupType.RosterActions)
        actions = action_group.get_available_actions(obj=roster_member)

        return ObjectDetailDTO(
            id=sqid_encode(roster_member.id),
            object_type=ObjectTypes.Roster,
            state=roster_member.state.name,
            title=roster_member.name,
            fields=[f for f in fields if f is not None],
            actions=actions,
            created_at=roster_member.created_at,
            updated_at=roster_member.updated_at,
            relations=[],
        )

    @classmethod
    def to_list_dto(cls, roster_member: Roster) -> ObjectListDTO:
        # Generate profile photo URLs if available
        profile_photo_field = None
        if roster_member.profile_photo:
            s3_client: S3Client = cls.registry.dependencies["s3_client"]
            photo_url = s3_client.generate_presigned_download_url(
                key=roster_member.profile_photo.file_key, expires_in=3600
            )
            thumbnail_url = (
                s3_client.generate_presigned_download_url(
                    key=roster_member.profile_photo.thumbnail_key, expires_in=3600
                )
                if roster_member.profile_photo.thumbnail_key
                else None
            )
            profile_photo_field = ObjectFieldDTO(
                key="profile_photo",
                value=ImageFieldValue(url=photo_url, thumbnail_url=thumbnail_url),
                label="Profile Photo",
                editable=False,
            )

        fields = [
            profile_photo_field,
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
            (
                ObjectFieldDTO(
                    key="facebook_handle",
                    value=(StringFieldValue(value=roster_member.facebook_handle)),
                    label="Facebook",
                    editable=False,
                )
                if roster_member.facebook_handle
                else None
            ),
            (
                ObjectFieldDTO(
                    key="tiktok_handle",
                    value=(StringFieldValue(value=roster_member.tiktok_handle)),
                    label="TikTok",
                    editable=False,
                )
                if roster_member.tiktok_handle
                else None
            ),
            (
                ObjectFieldDTO(
                    key="youtube_channel",
                    value=(StringFieldValue(value=roster_member.youtube_channel)),
                    label="YouTube",
                    editable=False,
                )
                if roster_member.youtube_channel
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
