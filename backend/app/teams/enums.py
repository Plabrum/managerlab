from enum import StrEnum


class TeamActions(StrEnum):
    """Team actions."""

    delete = "team.delete"
    invite_user = "team.invite_user"
