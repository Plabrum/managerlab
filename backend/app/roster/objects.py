from sqlalchemy.orm import joinedload
from typing import List

from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectFieldDTO,
    FieldType,
    ColumnDefinitionDTO,
    StringFieldValue,
    ImageFieldValue,
)
from app.objects.services import get_filter_by_field_type
from app.roster.enums import RosterStates
from app.roster.models import Roster
from app.client.s3_client import S3Client


class RosterObject(BaseObject):
    object_type = ObjectTypes.Roster
    model = Roster

    # Title/subtitle configuration
    title_field = "name"
    subtitle_field = "instagram_handle"
    state_field = "state"

    # Action groups
    top_level_action_group = ActionGroupType.TopLevelRosterActions

    # Load options
    load_options = [joinedload(Roster.user), joinedload(Roster.profile_photo)]

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
            key="email",
            label="Email",
            type=FieldType.Email,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="instagram_handle",
            label="Instagram",
            type=FieldType.String,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.String),
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
        ColumnDefinitionDTO(
            key="state",
            label="Status",
            type=FieldType.Enum,
            sortable=True,
            filter_type=get_filter_by_field_type(FieldType.Enum),
            default_visible=True,
            available_values=[e.name for e in RosterStates],
            editable=False,
            include_in_list=True,
        ),
    ]

    @classmethod
    def get_custom_fields(cls, roster_member: Roster) -> List[ObjectFieldDTO]:
        """Add custom fields for profile photo and conditional social media handles."""
        fields = []

        # Profile photo with S3 URL generation
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
            fields.append(
                ObjectFieldDTO(
                    key="profile_photo",
                    value=ImageFieldValue(url=photo_url, thumbnail_url=thumbnail_url),
                    label="Profile Photo",
                    editable=False,
                )
            )

        # Conditional social media handles (only if present)
        if roster_member.facebook_handle:
            fields.append(
                ObjectFieldDTO(
                    key="facebook_handle",
                    value=StringFieldValue(value=roster_member.facebook_handle),
                    label="Facebook",
                    editable=False,
                )
            )

        if roster_member.tiktok_handle:
            fields.append(
                ObjectFieldDTO(
                    key="tiktok_handle",
                    value=StringFieldValue(value=roster_member.tiktok_handle),
                    label="TikTok",
                    editable=False,
                )
            )

        if roster_member.youtube_channel:
            fields.append(
                ObjectFieldDTO(
                    key="youtube_channel",
                    value=StringFieldValue(value=roster_member.youtube_channel),
                    label="YouTube",
                    editable=False,
                )
            )

        return fields
