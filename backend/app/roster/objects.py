from sqlalchemy.orm import joinedload

from app.actions.enums import ActionGroupType
from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    FieldType,
    ObjectColumn,
)
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

    @staticmethod
    def _format_profile_photo(roster_member: Roster):
        """Generate S3 presigned URLs for profile photo."""
        if not roster_member.profile_photo:
            return None

        s3_client: S3Client = RosterObject.registry.dependencies["s3_client"]
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
        return {"url": photo_url, "thumbnail_url": thumbnail_url}

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
            key="email",
            label="Email",
            type=FieldType.Email,
            value=lambda obj: obj.email,
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
            value=lambda obj: obj.instagram_handle,
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
            value=lambda obj: obj.state,
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
            value=lambda obj: RosterObject._format_profile_photo(obj),
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
            value=lambda obj: obj.facebook_handle,
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
            value=lambda obj: obj.tiktok_handle,
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
            value=lambda obj: obj.youtube_channel,
            sortable=True,
            default_visible=True,
            editable=False,
            nullable=True,
            include_in_list=True,
        ),
    ]
